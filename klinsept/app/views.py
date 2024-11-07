from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from app.models import User, Product
from .serializers import UserSerializer, ProductSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings

#----------------------------REGISTER AND LOGIN USER ---------------------------------#

@api_view(['POST'])
def signUp(request):
    try:
        data = request.data
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        user = User(
            first_name=firstName,
            last_name=lastName,
            email=email,
            phone_number=phone,
        )
        user.set_password(password)
        user.save()

        # Return new user serialized data
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Login user
@api_view(['POST'])
def Login(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')

        user = User.objects.get(email=email)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            return Response({
                "Message": "Login Successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Request OTP for password reset
@api_view(["POST"])
def password_reset_otp(request):
    try:
        data = request.data
        email = data.get("email")

        user = get_object_or_404(User, email=email)

        user.set_otp()

        # Send OTP
        subject = "Your Password Reset OTP"
        message = f"Your OTP for password reset is: {user.otp}. It expires in 2 minutes."
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

        return Response({"Message": "OTP sent to your email."})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Verify OTP for password reset
@api_view(['POST'])
def verify_otp(request):
    try:
        data = request.data
        email = data.get("email")
        otp = data.get("otp")
        new_password = data.get("new_password")

        user = get_object_or_404(User, email=email)

        if user.otp == otp and user.is_otp_valid():

            # Validate the new password
            if not new_password or len(new_password) < 8:
                return Response({
                    "error": "Password must be at least 8 characters long"
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)

            # Clear OTP from the database
            user.otp = None
            user.otp_expiration = None
            user.save()

            return Response({"Message": "Password reset successfully"})
        else:
            return Response({
                "error": "Invalid or Expired OTP, retry again"
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Logout
# Implement token blocklist (not implemented in the original request)
@api_view(['POST'])
def Logout(request):
    try:
        # You can implement token blocklist logic here
        return Response({"Message": "Logged out successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#----------------------------PRODUCTS------------------------------------------#

class ProductPagination(PageNumberPagination):
    page_size = 10  # Number of products per page
    page_size_query_param = 'page_size'  # Allow client to change page size with ?page_size=5
    max_page_size = 100  # Limit the maximum page size

@api_view(['GET'])
def getProducts(request):
    try:
        products = Product.objects.all()
        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

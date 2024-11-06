from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from app.models import User,Product
from .serializers import UserSerializer,ProductSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings






#----------------------------REGISTER AND LOGIN USER ---------------------------------#
@api_view(['POST'])
def signUp(request):
    data = request.data
    fistName = data.get('firstName')
    lastName = data.get('lastName')
    email = data.get('email')
    phone = data.get('phone')
    location = data.get('location')
    password = data.get('password')

    # check if the email is already registered
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
    
    # else create a new user
    user = User(
        first_name=fistName,
        last_name=lastName,
        email=email,
        phone_number=phone,
        location=location,
    )
    user.set_password(password)
    user.save()
    # return new user serialized data
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# login user
@api_view(['POST'])
def Login(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')

    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            return Response({

                "Message":"Login Successful",
                "access_token":str(refresh.access_token),
                "refresh_token":str(refresh),
                "user":(serializer.data)
            },status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    

# request_otp
@api_view(["POST"])
def password_reset_otp(request):
    data = request.data
    email = data.get("email")
    
    # get user and return a 404 if not found
    # change to a custom try and catch is a custom error message is needed
    user = get_object_or_404(User,email=email)

    user.set_otp()

    # send otp
    subject = "Your Password Reset OTP"
    message = f"Your OTP for password reset is : {user.otp}. It expires in 2 minutes"
    send_mail(subject,message,settings.EMAIL_HOST_USER,[user.email])

    return Response({"Message":"OTP sent to your email."})
    
 
# verify_sent_otp
@api_view(['POST'])
def verify_otp(request):
    data = request.data
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    user = get_object_or_404(User,email=email)

    if user.otp == otp and user.is_otp_valid():

        # validate the new password set 
        if not new_password or len(new_password) < 8:
            return Response({
                "error":"password must be atleast of 8 characters long"
            },status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)

        # clear the otp from the database
        user.otp=None
        user.otp_expiration=None
        user.save()

        return Response({"Message":"Password reset successfully"})
    
    else:
        return Response({
            "error":"Invalid or Expired OTP, Retry again"
        },status=status.HTTP_400_BAD_REQUEST)







#----------------------------PRODUCTS------------------------------------------#
class ProductPagination(PageNumberPagination):
    page_size = 10  # Number of products per page
    page_size_query_param = 'page_size'  # Allow client to change page size with ?page_size=5
    max_page_size = 100  # Limit the maximum page size

@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    paginator = ProductPagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)





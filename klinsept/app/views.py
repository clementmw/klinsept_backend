from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from app.models import User, Product,Order,OrderItem,Payment,GuestUser,ShippingAddress
from .serializers import UserSerializer, ProductSerializer,OrderItemSerializer,OrderSerializer,PaymentSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed
import jwt
from datetime import datetime, timedelta, timezone
from django.utils.timezone import now, timedelta
from decouple import config
from app.utility import otp_mail,generate_tracking_id,send_email
from django.template.loader import render_to_string
# from django.utils.html import strip_tags



#----------------------------REGISTER AND LOGIN USER ---------------------------------#
# Register new user 
@api_view(['POST'])
def RegisterUser(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
def LoginUser(request):
    email = request.data['email']
    password = request.data['password']

    user = User.objects.filter(email=email).first()
    if user is None:
        raise AuthenticationFailed("User Not Found")
    
    if not user.check_password(password):
        raise AuthenticationFailed("Incorrect Password")
    
    payload = {
        'id':user.id,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=60),
        'iat': datetime.now(timezone.utc)
    }
    # put secret in .env 
    token = jwt.encode(payload,config("SECRET"),algorithm='HS256')
    # return token via cookies

    response = Response()
    response.set_cookie(key='jwt', value=token, httponly=True,secure=True) #secure true for htts request 
    response.data = {
        'jwt':token
    }
    return response

# GETCOOKIE
@api_view(['GET'])
def get_cookie(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed("Unauthenticated")
    
    try:
        payload = jwt.decode(token,config("SECRET"),algorithms=['HS256'])
    
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Unauthenticated")

    user = User.objects.filter(id=payload['id']).first()
    serializer = UserSerializer(user)
    return Response(serializer.data)



#----------------------------FORGET PASSWORD ROUTE ---------------------------------#

# Request OTP for password reset
@api_view(["POST"])
def password_reset_otp(request):
    try:
        data = request.data
        email = data.get("email")

        user = get_object_or_404(User, email=email)

        user.set_otp()

        # # Send OTP
        # subject = "Your Password Reset OTP"
        # message = f"Your OTP for password reset is: {user.otp}. It expires in 2 minutes."
        # send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        otp_mail(user.otp,user.email)

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
@api_view(['POST'])
def Logout(request):
    response = Response()
    response.delete_cookie('jwt')
    response.data = {
        'Message':"Logout Successfull"
    }
    return response
    
#----------------------------PRODUCTS------------------------------------------#
# get all products
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
    
# get all products by id
@api_view(['GET'])
def get_product_by_id(request,id):
    try:
        products = get_object_or_404(Product,id=id)
        serializer = ProductSerializer(products)
        return Response(serializer.data,status=status.HTTP_200_OK)

    except Exception as e:
        return Response ({'error':str(e),status:status.HTTP_500_INTERNAL_SERVER_ERROR})


# get related products 
@api_view(['GET'])
def related_products(request,id):
    try:
        products = get_object_or_404(Product,id=id)
        category = Product.objects.filter(category=products.category).exclude(id=products.id)

        serializer = ProductSerializer(category, many=True)
        
        return Response(serializer.data)
    
    except Product.DoesNotExist:
        return Response({"message": "Product not found"}, status=404)
    
    except Exception as e:
        return Response({"message": "An error occurred while retrieving related products."}, status=500)    


#----------------------------------------contact the company using email --------------------------#
@api_view(['POST'])
def contact(request):
    pass


#--------------------------------------------Order items ----------------------------------------#
# add to cart
@api_view(['POST'])
def add_to_cart(request):
    try:
        data = request.data
        product_id = data.get('product_id')
        quantity = data.get('quantity',1) #default product is one 

        product = get_object_or_404(Product, id=product_id)
        # check the product stock
        if product.stock < quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the product is already in the user's cart
        cart_item, created = OrderItem.objects.get_or_create(
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )

        if not created:
            # If the product is already in the cart, update the quantity
            cart_item.quantity += quantity
            cart_item.line_total = cart_item.quantity * cart_item.price
            cart_item.save()
    #   reduce the items in the product stock
        product.stock -= quantity
        product.save()

        serializer = OrderItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK) #to send serilized data using id to get cart items 

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# get items in cart
# to be fixed 
@api_view(['GET'])
def get_cart_items(request):
    try:
        cart_items = OrderItem.objects.all()
        serializer = OrderItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# remove from cart
@api_view(['DELETE'])
def remove_from_cart(request, id):
    try:
        cart_item = get_object_or_404(OrderItem, id=id)
        cart_item.delete()
        cart_items = OrderItem.objects.all()
        serializer = OrderItemSerializer(cart_items, many=True)
        return Response({'cart':serializer.data,'message':'Item removed from cart successfully'},
                            status=status.HTTP_200_OK
                        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_order(request):
    try:
        data = request.data
        token = request.COOKIES.get('jwt')
        user = None
        guest_user = None
        if token:
            try:
                payload = jwt.decode(token, config('SECRET'), algorithms=['HS256'])
                user = User.objects.filter(id=payload['id']).first()
                print(f"Authenticated user found: {user}")
            except jwt.ExpiredSignatureError:
                return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.InvalidTokenError:
                return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user:
            guest_first_name = request.data.get('guest_FirstName')
            guest_last_name = request.data.get('guest_LastName')
            guest_phone = request.data.get('guest_phone')
            guest_email = data.get('guest_email')

            if not guest_email:
                return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)
            
            validator = EmailValidator()
            try:
                validator(guest_email)
            except ValidationError:
                return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)
            
            existing_user = GuestUser.objects.filter(email=guest_email).first()
            if existing_user:
                # Use the existing user instead of creating a guest user
                guest_user = existing_user
                print(f"Using existing registered user for email: {guest_email}")
            else:
                # Create a new guest user if not found
                guest_user = GuestUser.objects.create(
                    email=guest_email,
                    first_name=guest_first_name,
                    last_name=guest_last_name,
                    phone_number=guest_phone
                )

        print("Shipping Address Creating")

        if user:
            shipping_address = ShippingAddress.objects.create(
                user=user,
                street_address=data.get('address'),
                city=data.get('city'),
                state=data.get('state'),
                zip_code=data.get('zip_code'),
                country=data.get('country')
            )
        elif guest_user:
            shipping_address = ShippingAddress.objects.create(
                guest_user=guest_user,
                street_address=data.get('address'),
                city=data.get('city'),
                state=data.get('state'),
                zip_code=data.get('zip_code'),
                country=data.get('country')
            )
        else:
            return Response({"error": "User or guest user must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        print(f"Shipping Address Created: {shipping_address}")

        order_item_id = data.get('order_item_id', [])
        if not order_item_id:
            return Response({"error": "No order items provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the existing OrderItems by their IDs
        order_items = OrderItem.objects.filter(id__in=order_item_id)

        # If any of the order items are not found, return an error
        if len(order_items) != len(order_item_id):
            return Response({"error": "Some order items not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order with the shipping address and total amount
        total_price = sum(item.line_total for item in order_items)  # Calculate the total amount for the order
        order = Order.objects.create(
            user=user,
            guest_user=guest_user,
            shipping_address=shipping_address,
            total_price=total_price  # Use the total amount calculated from the order items
        )
        order.tracking_id = generate_tracking_id()

        # Add order items to the order
        order.items.set(order_items)  # Set the order items for this order
    
        order.save()

        # Serialize and return the order data
        serializer = OrderSerializer(order)
        return Response({"order": serializer.data, "order_id": order.id}, status=status.HTTP_201_CREATED)
        

       
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# get order related to the email
@api_view(['GET'])
def get_order(request):
    # Retrieve the order ID from the query parameters
    order_id = request.query_params.get("order_id")

    if not order_id:
        return Response({"error": "Order ID is required in query parameters"}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the order based on the provided order ID
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize and return the order data
    serialized = OrderSerializer(order)
    return Response(serialized.data, status=status.HTTP_200_OK)

# -------------------------------------------------------------- send order to email -----------------------------------#
@api_view(['POST'])
def send_order_confirmation_email(request):
    order_id = request.data.get("order_id")
    if not order_id:
        return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the order and associated data
        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order)

        # Render the HTML content for the email using the template
        html_content = render_to_string("emails/order_confirmation.html", {
            "user_name": order.user.first_name if order.user else order.guest_user.first_name,
            "tracking_no": order.tracking_id,
            "order_items": serializer.data['items'],
            "total_price": order.total_price,
            'zip_code': order.shipping_address.zip_code,
            'country': order.shipping_address.country,
            'city':order.shipping_address.city,
            'state': order.shipping_address.state,
            'street_address': order.shipping_address.street_address,
            'shipping_cost':order.shipping_cost,
            'tax':order.tax
            
        })

        # Send the email using the utility function
        recipient_email = order.user.email if order.user else order.guest_user.email
        send_email(
            subject="Order Confirmation - Klinsept",
            message="",
            html_content=html_content,
            recipient_list=[recipient_email]
        )

        return Response({"message": "Order confirmation email sent successfully"}, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ---------------------------------------------------------------- Payment Routes -----------------------------------------------#
@api_view(['POST'])
def create_payment(request):
    data = request.data()
    try:
        order_id = request.get(order_id)
        check_order = Order.objects.filter(id=order_id).first()
        if not check_order:
            return Response({"Error":"Order ID is Required"},status=status.HTTP_400_BAD_REQUEST)

        payment_method = data.get('payment_method', 'Card')  # Default to "Card" if not provided
        status = data.get('status', 'Pending')  # Set default status if not provided

        payment = Payment.objects.create(
            user=check_order.user,
            ShippingAddress=check_order.shipping_address,
            order=check_order,
            payment_method=payment_method,
            total_price=check_order.total_price,
            status=status,
            payment_date=timezone.now()

        )

        serializer = PaymentSerializer(payment)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------------------------------- check status on order and rollback --------------------------------------#
@api_view(["GET"])
def check_pending_orders(request):
    try:
        time_limit = now() - timedelta(minutes=1)
        pending_orders = Order.objects.filter(status='Pending', created_at__lte=time_limit)

        if pending_orders.exists():
            for order in pending_orders:
                # Rollback order by returning items to inventory
                for item in order.items.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save()

                # Delete the pending order
                order.delete()

            return Response({"message": "Rolled back orders."}, status=status.HTTP_200_OK)
        else:
            # If no orders found that are older than 1 hour
            return Response({"message": "No orders to rollback; all pending orders are within 1 hour."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
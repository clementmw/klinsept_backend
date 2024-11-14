from rest_framework import serializers
from .models import User, Category, Product, Order, Review, Payment, ShippingAddress,OrderItem,GuestUser
# from django.contrib.auth.hashers import make_password, check_password 

# to create serialized data for json 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number','password' ,'created_at']

        extra_kwargs = {
            'password': {"write_only":True}
        }
    def create(self,validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
        

class GuestUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestUser
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'created_at']
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    # We will use a SerializerMethodField to transform the category
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'price', 'stock', 'category', 'created_at', 'updated_at']

    def get_category(self, obj):
        return [obj.category.name]  
    
# orderitems serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Serialize product as part of the OrderItem, but don't include 'quantity' or other product-specific fields here

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'line_total']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id','street_address','city','state','zip_code','country']

# order serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)  # Serialize order items as part of the order
    user = UserSerializer(read_only=True)
    guest_user = GuestUserSerializer  # Serialize guest user as part of the order
    shipping_address = ShippingAddressSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user','guest_user', 'items','shipping_cost','tax', 'total_price','shipping_address','tracking_id']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model:Payment
        field = ['id','order','shipping_address','payment_method','user','total_price','status','payment_date']
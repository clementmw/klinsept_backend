from rest_framework import serializers
from .models import User,Category,Product,Order,Review,Payment,ShippingAddress

# to create serialized data for json 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','description']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    
    class Meta:
        model = Product
        fields = ['id','name','description','image','price','stock','category','created_at','updated_at']

from rest_framework import serializers
from .models import User, Category, Product, Order, Review, Payment, ShippingAddress

# to create serialized data for json 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
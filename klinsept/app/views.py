from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from app.models import User,Product
from .serializers import UserSerializer,ProductSerializer


# Create your views here.
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





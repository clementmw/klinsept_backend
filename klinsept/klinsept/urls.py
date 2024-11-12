"""
URL configuration for klinsept project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import getProducts,RegisterUser,LoginUser,password_reset_otp,verify_otp,Logout,get_product_by_id,contact,add_to_cart,get_cart_items,remove_from_cart,create_order,get_cookie,get_order

urlpatterns = [
    path('admin/', admin.site.urls), #to be changed and added api/v1.0 to be use with api keys
    # get all products
    path('api/v1.0/products/', getProducts, name='get_products'),
    # Get product by id
    path('api/v1.0/product/<int:id>',get_product_by_id,name="get_indivual_product"),    # signup user
    # register user
    path('api/v1.0/auth/signin/',RegisterUser,name='signUp_user'),
    # login 
    path('api/v1.0/auth/login/',LoginUser,name='login_user'),
    # get user cookie
    path('api/v1.0/auth/cookie/',get_cookie,name='login_user'),
    # get otp 
    path('api/v1.0/auth/otp/request/',password_reset_otp,name="password_reset_otp"),
    # Reset password and confirm otp
    path('api/v1.0/auth/otp/confirm/',verify_otp, name = "otp_confirmation"),
    # Logout user
    path('api/v1.0/auth/logout/',Logout, name = "otp_confirmation"),
    # Contact client
    path('api/v1.0/contact',contact,name='contact company'),
    # add items to cart
    path('api/v1.0/cart/add/',add_to_cart, name='add_to_cart'),
    # get items in cart
    path('api/v1.0/cart/', get_cart_items, name='get_cart_items'),
    # remove items from cart
    path('api/v1.0/cart/remove/<int:id>', remove_from_cart, name='remove_from_cart'),
    # place order
    path('api/v1.0/order/', create_order, name='create_order'),
    # get order
    path('api/v1.0/user/order/',get_order, name='get_order'),

]

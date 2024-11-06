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
from app.views import getProducts,signUp,Login,password_reset_otp,verify_otp

urlpatterns = [
    path('admin/', admin.site.urls), #to be changed and added api/v1.0 to be use with api keys
    path('api/v1.0/products/', getProducts, name='get_products'),
    # signup user
    path('api/v1.0/auth/sigin/',signUp,name='signUp_user'),
    # login 
    path('api/v1.0/auth/login/',Login,name='login_user'),
    # get otp 
    path('api/v1.0/auth/otp/request/',password_reset_otp,name="password_reset_otp"),
    # Reset password and confirm otp
    path('api/v1.0/auth/otp/confirm/',verify_otp, name = "otp_confirmation")

]

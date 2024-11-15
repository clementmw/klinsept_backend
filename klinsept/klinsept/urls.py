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
from django.urls import path, re_path
from app.views import (
    getProducts, RegisterUser, LoginUser, password_reset_otp, verify_otp,
    Logout, get_product_by_id, contact, add_to_cart, get_cart_items,
    remove_from_cart, create_order, get_cookie, get_order, check_pending_orders,
    send_order_confirmation_email, related_products
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view setup
schema_view = get_schema_view(
    openapi.Info(
        title="KLINSEPT API",
        default_version='1.0.0',
        description="API documentation for Klinsept backend",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@klinsept.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

# API routes
urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    # Product endpoints
    path('api/v1.0/products/', getProducts, name='get_products'),
    path('api/v1.0/product/<int:id>/', get_product_by_id, name="get_individual_product"),
    path('api/v1.0/related_product/<int:id>/', related_products, name="get_related_products"),
    
    # Authentication endpoints
    path('api/v1.0/auth/signin/', RegisterUser, name='signUp_user'),
    path('api/v1.0/auth/login/', LoginUser, name='login_user'),
    path('api/v1.0/auth/cookie/', get_cookie, name='get_authentication_cookie'),
    path('api/v1.0/auth/otp/request/', password_reset_otp, name="_get_password_reset_otp"),
    path('api/v1.0/auth/otp/confirm/', verify_otp, name="otp_confirmation"),
    path('api/v1.0/auth/logout/', Logout, name="logout_user"),
    
    # Contact endpoint
    path('api/v1.0/contact/', contact, name='contact_company'),
    
    # Cart endpoints
    path('api/v1.0/cart/add/', add_to_cart, name='add_to_cart'),
    path('api/v1.0/cart/', get_cart_items, name='get_items_incart'),
    path('api/v1.0/cart/remove/<int:id>/', remove_from_cart, name='remove_items_from_cart'),
    
    # Order endpoints
    path('api/v1.0/order/', create_order, name='create_order'),
    path('api/v1.0/user/order/', get_order, name='get__individual_order'),
    path('api/v1.0/check-pending-orders/', check_pending_orders, name='check_pending_orders'),
    path('api/v1.0/send/email/', send_order_confirmation_email, name='send_email'),
]

# Swagger and ReDoc documentation endpoints
urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

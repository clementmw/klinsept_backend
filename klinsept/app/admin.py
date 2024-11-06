from django.contrib import admin
from .models import Product,Category

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','description','price','category')  # Fields to display in the list view
    search_fields = ['name']  # Add a search bar for product names
    list_filter = ('name','price','category')  # Filter products by price in the admin panel

admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    search_fields = ['name']
    list_filter = ['name']

admin.site.register(Category,CategoryAdmin)
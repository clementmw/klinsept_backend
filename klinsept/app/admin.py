from django.contrib import admin
from .models import Product,Category

# personalized the admin dashboard

admin.site.site_header = "KLINSEPT DASHBOARD "
admin.site.site_title = "Klinsept"
admin.site.index_title = "Welcome to Your your Dashboard"

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
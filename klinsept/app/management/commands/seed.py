import random
from django.core.management.base import BaseCommand
from app.models import Category, Product

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Seed categories
        categories = [
            "Electronics",
            "Books",
            "Clothing",
            "Home & Kitchen",
            "Sports & Outdoors"
        ]

        # Create categories in the database
        created_categories = []
        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            created_categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category_name}'))

        # Seed products with random categories
        products = [
            {"name": "Smartphone", "price": 699.99, "stock": 50},
            {"name": "Laptop", "price": 999.99, "stock": 30},
            {"name": "T-Shirt", "price": 19.99, "stock": 100},
            {"name": "Fiction Book", "price": 14.99, "stock": 200},
            {"name": "Kitchen Knife Set", "price": 49.99, "stock": 20}
        ]

        for product in products:
            # Randomly select a category for each product
            category = random.choice(created_categories)
            try:
                product_instance = Product.objects.create(
                    name=product['name'],
                    price=product['price'],
                    stock=product['stock'],
                    category=category
                )
                self.stdout.write(self.style.SUCCESS(f'Created product: {product["name"]} in category: {category.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create product: {product["name"]}, Error: {str(e)}'))


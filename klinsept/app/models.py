from django.db import models
from django.core.validators import RegexValidator,MaxValueValidator, MinValueValidator


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    location = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField(max_length=500, blank=True, null=True)  # Use URLField to store image links
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional fields for guest orders
    guest_name = models.CharField(max_length=50, null=True, blank=True)
    guest_email = models.EmailField(max_length=254, unique=True)
    guest_location = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} for {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],  # Ensures rating is between 1 and 5
        help_text="Rating should be between 1 and 5."
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')])
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"
    
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}"


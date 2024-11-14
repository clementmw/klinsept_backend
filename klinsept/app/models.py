from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from .utility import generate_otp
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from app.managers import CustomUserManager


class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=20)
    password = models.CharField(max_length=128, null=True, blank=True)
    username=None
    otp = models.CharField(max_length=7, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]

    def set_otp(self):
        self.otp = str(generate_otp())
        self.otp_expiration = timezone.now()
        self.save()

    def is_otp_valid(self):
        if self.otp_expiration:
            return timezone.now() < self.otp_expiration + timedelta(minutes=2)
        return False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    objects = CustomUserManager()  # Use the custom manager


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField(max_length=500, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class GuestUser(models.Model):
    first_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(max_length=254,unique=True)
    phone_number = models.CharField(max_length=20,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name},{self.last_name}"

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses',null=True,blank=True)
    guest_user = models.ForeignKey(GuestUser, on_delete=models.CASCADE, related_name='shipping_addresses', null=True, blank=True)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}"
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders',null=True)
    guest_user = models.ForeignKey(GuestUser, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE, related_name='orders',null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    status = models.CharField(max_length=50,choices=[('Paid','Paid'),('Pending','Pending')],default="Pending") 
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tracking_id = models.CharField(max_length=20,unique=True,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # to be added shipping cost and tax if provided by client

    def save(self, *args, **kwargs):
        # Calculate the subtotal (sum of line_total from all order items)
        if not self.total_price:
            order_subtotal = sum(item.line_total for item in self.items.all())
            # Add shipping cost and tax
            self.total_price = order_subtotal + self.shipping_cost + self.tax
        super().save(*args, **kwargs)
    
    def __str__(self):
        user_email = self.user.email if self.user else (self.guest_user.email if self.guest_user else "Guest")
        details = (
            f"Order ID: {self.id} | "
            f"User: {user_email} | "
            f"Status: {self.status} | "
            f"Total: ${self.total_price:.2f} | "
            f"Shipping Cost: ${self.shipping_cost:.2f} | "
            f"Tax: ${self.tax:.2f} | "
            f"Tracking ID: {self.tracking_id or 'Not assigned'}"
        )
        return details


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items',null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2,editable=False,default='0.00') #calculates the total price of the product*quantity
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def save(self, *args, **kwargs):
        # Calculate line_total as quantity * price before saving
        self.line_total = self.quantity * self.price  
        super().save(*args, **kwargs)
    

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments',null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE, related_name='payments',null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=100,default="Card")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user and not self.order.guest_user:
            raise ValueError("A payment must be associated with a user or guest user.")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],  # Ensures rating is between 1 and 5
        help_text="Rating should be between 1 and 5."
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



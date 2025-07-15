from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    is_active = models.BooleanField(default=True, help_text="Designates whether this user should be treated as active.")
    phone_number = models.CharField(max_length=15, null=True, blank=True, help_text="User's contact phone number.")
    address = models.TextField(null=True, blank=True, help_text="User's residential address.")
    logged_in = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    #new
    REQUIRED_FIELDS = ['username']  
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super(User, self).save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Discount percentage (e.g., 10 for 10%)")
    sales = models.PositiveIntegerField(default=0, help_text="Number of units sold")
    date_sold = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name
    @property
    def get_discounted_price(self):
        discounted_price = self.price - (self.price * self.discount_percentage/100)
        return round(discounted_price,2)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add default value



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
    ], default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.id}"
    
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def TokenCreate(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)    

from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone



class Product(models.Model):
    category = models.CharField(max_length=100, default='Vetements')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)


    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Client
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)  # Prix total
    order_date = models.DateTimeField(auto_now_add=True)  # Date de commande
    order_code = models.CharField(max_length=50, unique=True, editable=False, default=uuid.uuid4)
     

    def calculate_total(self):
        # Recalculer le total en fonction des OrderItems associés
        self.total_price = sum(item.total_price for item in self.order_items.all())
        self.save()

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = f"{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_code}  by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    livre = models.BooleanField(default=False)
    disponible = models.BooleanField(default=False)
    order_date = models.DateTimeField( default=timezone.now)  # Date de commande

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"        

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE,null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)            

    

class CustomUser(AbstractUser):
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"   


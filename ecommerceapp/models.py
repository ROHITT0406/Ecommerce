from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
import uuid
# Create your models here.
class Product(models.Model):
    product_img=models.ImageField(upload_to='product',blank=True,null=True)
    product_name=models.CharField (max_length=100)
    product_rating=models.ImageField(upload_to='rating',blank=True,null=True)
    product_count=models.IntegerField()
    product_price=models.FloatField()
    key_word=models.CharField( max_length=500)

    def __str__(self):
        return self.product_name
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    add_to_date=models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return f"{self.user.username}-{self.product.product_name}"

    @property
    def totalprice(self):
        return self.quantity * self.product.product_price
    @property
    def delivery_date(self):
        return self.add_to_date + timedelta(days=3)

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    order_id=models.CharField(max_length=100)
    order_date=models.DateTimeField( auto_now_add=True)
    quantity=models.PositiveIntegerField(default=1)
    delivery_date=models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_cancelled = models.BooleanField(default=False)


    def __str__(self):
        return f"Order by {self.user.username} - {self.product.product_name}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.full_name}, {self.city}"

class Orderdetails(models.Model):
    name=models.CharField(max_length=100)
    amount = models.CharField(max_length=100)
    order_id=models.CharField(max_length=100,blank=True)
    razorpay_payment_id=models.CharField(max_length=100,blank=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"
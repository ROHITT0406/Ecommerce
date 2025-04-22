from django.contrib import admin
from . models import Product,Cart,Order,Address,Orderdetails
# Register your models here.
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Orderdetails)
from rest_framework import serializers
from ecommerceapp.models import Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'


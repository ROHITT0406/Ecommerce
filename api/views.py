from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ecommerceapp.models import Product,Address,Order,Orderdetails,Cart
from .serializers import ProductSerializer



@api_view(['GET'])
def product(request):
    objs=Product.objects.all()
    serializer = ProductSerializer(objs,many=True)
    return Response(serializer.data)
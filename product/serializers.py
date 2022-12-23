from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'store']
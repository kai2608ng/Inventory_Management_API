from rest_framework import serializers
from .models import Product
from store.models import Store

class ProductSerializer(serializers.ModelSerializer):
    store = serializers.SlugRelatedField(queryset = Store.objects.all(), slug_field = 'name')

    class Meta:
        model = Product
        fields = ['name', 'store']
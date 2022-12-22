from rest_framework import serializers
from .models import Material, MaterialQuantity
from product.models import Product
from store.models import Store

class MaterialSerializer(serializers.ModelSerializer):
    store = serializers.SlugRelatedField(queryset = Store.objects.all(), slug_field = "name")

    class Meta:
        model = Material
        fields = ['name', 'price', 'store', 'max_capacity', 'current_capacity']

    def validate_max_capacity(self, value):
        if value < 0:
            raise serializers.ValidationError({"Please enter a valid value"})
        return value

    def validate_current_capacity(self, value):
        if value < 0:
            raise serializers.ValidationError({"Please enter a valid value"})
        return value

class MaterialQuantitySerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(queryset = Product.objects.all(), slug_field = 'name')
    material = serializers.SlugRelatedField(queryset = Material.objects.all(), slug_field = 'name')

    class Meta:
        model = MaterialQuantity
        fields = ['product', 'material', 'quantity']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Please enter a valid value")
        return value
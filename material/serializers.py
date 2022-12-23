from rest_framework import serializers
from .models import Material, MaterialQuantity
from product.models import Product

class MaterialSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()
    percentage_of_capacity = serializers.DecimalField(max_digits = 3, decimal_places = 2, read_only = True)

    class Meta:
        model = Material
        fields = ['id', 'name', 'price', 'store', 'max_capacity', 'current_capacity', 'percentage_of_capacity']

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
        fields = ['id', 'product', 'material', 'quantity']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Please enter a valid value")
        return value

class MaterialsSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(required = True)
    id = serializers.IntegerField(required = True)

    class Meta:
        model = Material
        fields = ['id', 'quantity']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Please enter a valid value")
        
        return value

    def validate_id(self, value):
        try:
            Material.objects.get(pk = value)
        except Material.DoesNotExist:
            raise serializers.ValidationError("Material doesn't exists!")

        return value

    def validate(self, data):
        material_id = data['id']
        quantity = data['quantity']
        
        # Check whether material exists
        try:
            material = Material.objects.get(pk = material_id)
        except Material.DoesNotExist:
            raise serializers.ValidationError({'material': "Material doesn't exists!"})

        # Check whether restock quantity will exceed max_capacity
        if material.current_capacity + quantity > material.max_capacity:
            raise serializers.ValidationError({'error_messages': "Invalid restock quantity"})

        return data

    def create(self, validated_data):
        material_id = validated_data['id']
        quantity = validated_data['quantity']
        material = Material.objects.get(pk = material_id)
        material.current_capacity += quantity
        return material.save()

class RestockSerializer(serializers.Serializer):
    materials = MaterialsSerializer(required = True, many = True)
    total_price = serializers.DecimalField(max_digits = 10, decimal_places = 2)

    def save(self):
        materials = self.validated_data.pop('materials')
        serializer = MaterialsSerializer(data = materials, many = True)

        # Check validation of the data
        if serializer.is_valid():
            serializer.save()

class InventorySerializer(serializers.ModelSerializer):
    percentage_of_capacity = serializers.DecimalField(max_digits = 3, decimal_places = 2)

    class Meta:
        model = Material
        fields = ['id', 'max_capacity', 'current_capacity', 'percentage_of_capacity']
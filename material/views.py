from django.shortcuts import render
from rest_framework import viewsets
from .models import Material, MaterialQuantity
from .serializers import (
    MaterialSerializer, MaterialQuantitySerializer, MaterialsSerializer, RestockSerializer,
    InventorySerializer
)
from store.models import Store
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import F, Sum, ExpressionWrapper, FloatField, Func
import json

class MaterialViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Only using user's own materials
    def get_queryset(self):
        store = Store.objects.get(user = self.request.user)
        return Material.objects.filter(store = store)

    def create(self, request):
        store = Store.objects.get(user = request.user)
        name = request.data.get('name')
        price = request.data.get('price')
        max_capacity = request.data.get("max_capacity", 0)
        current_capacity = request.data.get("current_capacity", 0)

        # Check duplication of the material name
        if Material.objects.filter(store = store, name = name).exists():
            return Response({"error_messages": "Material existed!"})

        data = {
            'name': name,
            'price': price,
            'max_capacity': max_capacity,
            'current_capacity': current_capacity
        }

        serializer = MaterialSerializer(data = data)

        # Check validation of the data
        if serializer.is_valid():
            serializer.save(store = store)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors)

    def update(self, request, pk):
        store = Store.objects.get(user = request.user)
        name = request.data.get('name')
        price = request.data.get('price')
        max_capacity = request.data.get("max_capacity", 0)

        data = {
            'name': name,
            'price': price,
            'max_capacity': max_capacity,
        }

        # Update material
        material = Material.objects.get(pk = pk)
        serializer = MaterialSerializer(material, data = data)

        # Check validation of the data
        if serializer.is_valid():
            serializer.save(store = store)
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response(serializer.errors)

    @action(detail = False, methods = ['get', 'post'])
    def restock(self, request):
        if request.method == "GET":
            materials = self.get_queryset()
            # Calculate the quantity of each material needed to be restock and only get those that need to be restocked
            restock_material = materials.annotate(quantity = F('max_capacity') - F('current_capacity')).filter(quantity__gt = 0)

            # Check is there anything to restock
            if not restock_material.exists():
                return Response({'messages': 'Nothing to restock!'})

            serializer = MaterialsSerializer(restock_material.values('id', 'quantity'), many = True)
            total_price = round(restock_material.aggregate(total_price = Sum(F('quantity') * F('price'))).get('total_price'), 2)
            return Response({'materials': serializer.data, 'total_price': total_price})

        elif request.method == "POST":
            # replace single quote to double quote to parsing from json.load()
            materials = [json.loads(material.replace('\'', "\"")) for material in request.data.getlist("materials")]
            total_price = request.data.get("total_price", 0)

            data = {
                'materials': materials,
                'total_price': total_price,
            }

            serializer = RestockSerializer(data = data)

            # Check validation of the data
            if serializer.is_valid():
                # Update material current_capacity
                serializer.save()
                return Response({"message": "Restock successfully"})

            else:
                return Response(serializer.errors)

    @action(detail = False, methods = ['get'])
    def inventory(self, request):
        queryset = self.get_queryset()

        # Change current_capacity and max_capacity to float
        template = "%(function)s(%(expressions)s AS FLOAT)"
        current_capacity = Func(F('current_capacity'), function = "CAST", template = template)
        max_capacity = Func(F('max_capacity'), function = "CAST", template = template)

        materials = queryset.annotate(
            percentage_of_capacity = ExpressionWrapper(
                current_capacity / max_capacity, output_field = FloatField())
        )
        inventories = materials.values('id', 'max_capacity', 'current_capacity', 'percentage_of_capacity')
        serializer = InventorySerializer(inventories, many = True)
        return Response(serializer.data)

class MaterialQuantityViewSet(viewsets.ModelViewSet):
    queryset = MaterialQuantity.objects.all()
    serializer_class = MaterialQuantitySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
        

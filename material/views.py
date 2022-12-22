from django.shortcuts import render
from rest_framework import viewsets
from .models import Material, MaterialQuantity
from .serializers import MaterialSerializer, MaterialQuantitySerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class MaterialQuantityViewSet(viewsets.ModelViewSet):
    queryset = MaterialQuantity.objects.all()
    serializer_class = MaterialQuantitySerializer

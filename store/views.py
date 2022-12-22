from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Store
from .serializers import StoreSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    def create(self, request):
        username = request.data.get('user')
        if hasattr(User.objects.get(username = username), 'store_entries'):
            return Response({'error_messages': "User already created a store!"})

        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors)


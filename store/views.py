from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Store
from .serializers import StoreSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        # Check whether user has already created store
        if hasattr(User.objects.get(username = request.user), 'store_entries'):
            return Response({'error_messages': "User already created a store!"})
       
        serializer = self.get_serializer(data = request.data)

        # Check validation of the data
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors)

    # Only user that contains that store can delete that store
    def destroy(self, request, pk = None):
        user = User.objects.get(pk = pk)

        if request.user == user:
            store = Store.objects.get(user = user)
            store.delete()
            return Response({"messages": "Store deleted!"}, status = status.HTTP_204_NO_CONTENT)
        
        return Response({"error_messages": "Invalid User"})

    # Only user that contains that store can update that store
    def update(self, request, pk = None):
        user = User.objects.get(pk = pk)

        if request.user == user:
            store = Store.objects.get(user = user)
            serializer = StoreSerializer(store, data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

        return Response({"error_messages": "Invalid user"})

    def partial_update(self, request, pk = None):
        user = User.objects.get(pk = pk)

        if request.user == user:
            store = Store.objects.get(user = user)
            serializer = StoreSerializer(store, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

        return Response({"error_messages": "Invalid user"})

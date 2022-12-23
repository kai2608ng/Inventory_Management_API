from rest_framework import serializers
from .models import Store
from django.contrib.auth import get_user_model

User = get_user_model()

class StoreSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Store
        fields = ['id', 'name', 'user']


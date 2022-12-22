from rest_framework import serializers
from .models import Store
from django.contrib.auth import get_user_model

User = get_user_model()

class StoreSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field = "username", queryset = User.objects.all())

    class Meta:
        model = Store
        fields = ['name', 'user']

    def create(self, validated_data):
        name = validated_data.get('name')
        user = validated_data.get('user')
        return Store.objects.create(name = name, user = user)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance

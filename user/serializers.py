from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(
        write_only = True,
        required = True,
        style = {'input_type': 'password'}
    )
    repassword = serializers.CharField(
        write_only = True,
        required = True,
        style = {'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'repassword', 'email']
        extra_kwargs = {'email': {'help_text': 'Email is optional'}}

    def validate(self, data):
        password = data.get('password')
        repassword = data.get('repassword')
        if password != repassword:
            raise serializers.ValidationError({
                'password': 'Please enter same password',
                'repassword': 'Please enter same password'})
        return data

    def validate_username(self, value):
        if User.objects.filter(username = value).exists():
            raise serializers.ValidationError({'username': "Username already exists!"})
        return value

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        return User.objects.create_user(username = username, password = password)
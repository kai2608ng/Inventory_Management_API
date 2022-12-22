from django.test import TestCase
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from django.urls import reverse
from rest_framework import status

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        User.objects.create_user(username = "admin1", password = "password123")
        self.assertEqual(User.objects.count(), 1)
        User.objects.create_user(username = "admin2", password = "password123")
        self.assertEqual(User.objects.count(), 2)

class UserSerializerTest(TestCase):
    def test_serialize(self):
        user = User.objects.create_user(username = "admin", password = 'password123')
        serializer = UserSerializer(user)
        self.assertEqual(serializer.data['username'], user.username)

    def test_deserialize(self):
        data = {'username': 'admin', 'password': 'password123', 'repassword': 'password123'}
        serializer = UserSerializer(data = data)
        self.assertTrue(serializer.is_valid())

    def test_duplicated_username_cannot_be_created(self):
        data = {'username': 'admin', 'password': 'password123', 'repassword': 'password123'}
        serializer = UserSerializer(data = data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        data = {'username': 'admin', 'password': 'password123', 'repassword': 'password123'}
        serializer = UserSerializer(data = data)
        self.assertFalse(serializer.is_valid())

class UserViewTest(APITestCase):
    def test_get_method_not_allow_in_login(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_to_login(self):
        # Sign Up
        User.objects.create_user(username = "admin", password = 'password123')

        url = reverse('login')        
        response = self.client.post(url, data = {'username': 'admin', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_method_not_allow_in_sign_up(self):
        url = reverse('signup')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_in_sign_up(self):
        url = reverse('signup')
        data = {
            'username': 'admin',
            'password': 'password123',
            'repassword': 'password123',
        }

        response = self.client.post(url, data = data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
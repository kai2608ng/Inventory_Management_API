from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Store
from django.db import IntegrityError
from .serializers import StoreSerializer
from django.urls import reverse

User = get_user_model()

class StoreModelTest(TestCase):
    def setUp(self):
        User.objects.create_user(username = 'admin', password = 'password123')

    def test_create_store(self):
        user = User.objects.get(pk = 1)
        Store.objects.create(name = 'store1', user = user)
        self.assertEqual(Store.objects.count(), 1)

    def test_user_cannot_create_2_store_and_above(self):
        user = User.objects.get(pk = 1)
        Store.objects.create(name = 'store1', user = user)
        with self.assertRaises(IntegrityError):
            Store.objects.create(name = 'store2', user = user)

class StoreSerializerTest(TestCase):
    def setUp(self):
        User.objects.create_user(username = "admin", password = "password123")

    def test_serialize(self):
        user = User.objects.get(pk = 1)
        store = Store.objects.create(name = "store1", user = user) 
        serializer = StoreSerializer(store)
        self.assertEqual(serializer.data['name'], 'store1')

    def test_deserialize(self):
        user = User.objects.get(pk = 1)
        serializer = StoreSerializer(data = {'name': 'store1', 'user': user})
        self.assertTrue(serializer.is_valid())

    def test_update_store(self):
        user = User.objects.get(pk = 1)
        serializer = StoreSerializer(data = {'name': 'store1', 'user': user})
        self.assertTrue(serializer.is_valid())
        serializer.save(user = user)
        store = Store.objects.get(pk = 1)
        serializer = StoreSerializer(store, data = {'name': 'new_store'}, partial = True)
        self.assertTrue(serializer.is_valid())
        serializer.save(user = user)
        self.assertEqual(Store.objects.get(pk = 1).name, 'new_store')

class StoreViewTest(APITestCase):
    def setUp(self):
        User.objects.create_user(username = "admin", password = 'password123')

    # Utils function for force_authentication
    def force_authentication(self):
        user = User.objects.get(pk = 1)
        self.client.force_authenticate(user = user)

    # Utils function for creating store
    def create_store(self, name, user):
        url = reverse('store-list')
        data = {
            'name': name,
            'user': user
        }

        return self.client.post(url, data)

    def test_list_store(self):
        # authentication
        self.force_authentication()

        url = reverse('store-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_store(self):
        # authentication
        self.force_authentication()

        # Create store
        name = 'store1'
        user = User.objects.get(pk = 1)
        response = self.create_store(name, user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Store.objects.count(), 1)

    def test_retrive_store(self):
        # authentication
        self.force_authentication()
        
        # Create store
        name = 'store1'
        user = User.objects.get(pk = 1)
        response = self.create_store(name, user)
        
        # Retrieve store
        url = reverse('store-detail', args = (1, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_partial_update_store(self):
        # authentication
        self.force_authentication()

        # Create store
        name = 'store1'
        user = User.objects.get(pk = 1)
        response = self.create_store(name, user)

        # Partial update store
        url = reverse('store-detail', args = (1, ))
        data = {
            'name': 'new_store'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Store.objects.get(pk = 1).name, 'new_store')

    def test_delete_store(self):
        # authentication
        self.force_authentication()

        # Create store
        name = 'store1'
        user = User.objects.get(pk = 1)
        response = self.create_store(name, user)
        
        # Delete store
        url = reverse('store-detail', args = (1, ))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Store.objects.count(), 0)
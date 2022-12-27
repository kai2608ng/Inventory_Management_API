from .base_test import BaseMaterialTest
from ..models import Material
from store.models import Store
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError
from ..serializers import MaterialSerializer
from rest_framework import status

User = get_user_model()

class MaterialModelTest(BaseMaterialTest):
    def test_create_material(self):
        store = Store.objects.get(pk = 1)
        Material.objects.create(name = "material1", price = 12.50, store = store)
        self.assertEqual(Material.objects.count(), 1)
        Material.objects.create(name = "material2", price = 12.50, store = store)
        self.assertEqual(Material.objects.count(), 2)

    def test_cannot_create_same_material_in_same_store(self):
        store = Store.objects.get(pk = 1)
        Material.objects.create(name = "material1", price = 12.50, store = store)
        self.assertEqual(Material.objects.count(), 1)
        # unique_together = ['name', 'store']
        with self.assertRaises(IntegrityError):
            Material.objects.create(name = "material1", price = 12.50, store = store)

class MaterialSerializerTest(BaseMaterialTest):
    def test_serialize(self):
        store = Store.objects.get(pk = 1)
        material = Material.objects.create(name = 'material1', price = 12.50, store = store)
        serializer = MaterialSerializer(material)
        self.assertEqual(serializer.data['name'], 'material1')

    def test_deserialize(self):
        store = Store.objects.get(pk = 1)
        data = {
            'name': 'material1',
            'price': 12.50,
            'store': store
        }
        serializer = MaterialSerializer(data = data)
        self.assertTrue(serializer.is_valid())

    def test_cannot_insert_negative_value_in_capacity(self):
        store = Store.objects.get(pk = 1)
        data = {
            'name': 'material1',
            'price': 12.50,
            'store': store,
            'max_capacity': -10,
            'current_capacity': -10,
        }
        serializer = MaterialSerializer(data = data)
        self.assertFalse(serializer.is_valid())

class MaterialViewTest(BaseMaterialTest):
    # Utils function for force authentication
    def force_authentication(self, user = None):
        if not user:
            user = User.objects.get(pk = 1)
        self.client.force_authenticate(user = user)

    # Utils function for creating a new material
    def create_material(self, name, store, price = 12.50, max_capacity = 0, current_capacity = 0):
        url = reverse('material-list')
        data = {
            'name': name,
            'price': price,
            'store': store,
            'max_capacity': max_capacity,
            'current_capacity': current_capacity
        }

        return self.client.post(url, data)

    def test_list_material(self):
        # authentication
        self.force_authentication()

        url = reverse('material-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_material(self):
        # authentication
        self.force_authentication()

        name = "material1"
        store = Store.objects.get(pk = 1)
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)

    def test_retrive_material(self):
        # authentication
        self.force_authentication()

        # Create material
        name = "material1"
        store = Store.objects.get(pk = 1)
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve material
        url = reverse('material-detail', args = (1, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_material(self):
        # authentication
        self.force_authentication()

        # Create material
        name = "material1"
        store = Store.objects.get(pk = 1)
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update material
        url = reverse('material-detail', args = (1, ))
        data = {
            'price': 12.50,
            'store': store,
            'max_capacity': 200,
            'current_capacity': 100
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m = Material.objects.get(pk = 1)
        self.assertEqual(m.max_capacity, 200)
        # Didn't change current_capacity
        self.assertEqual(m.current_capacity, 0)

    def test_delete_material(self):
        # authentication
        self.force_authentication()

        # Create material
        name = "material1"
        store = Store.objects.get(pk = 1)
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Delete material
        url = reverse('material-detail', args = (1, ))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Material.objects.count(), 0)

    def test_show_user_their_own_material_list(self):
        # authentication
        self.force_authentication()

        # Create material
        name = "material1"
        store = Store.objects.get(pk = 1)
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create material
        name = "material2"
        store = Store.objects.get(pk = 1)
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create new user
        user = User.objects.create_user(username = "admin2", password = "password123")
        self.force_authentication(user)
        Store.objects.create(name = 'store2', user = user)
        url = reverse('material-list')
        response = self.client.get(url)
        self.assertIn('[]', response.content.decode())
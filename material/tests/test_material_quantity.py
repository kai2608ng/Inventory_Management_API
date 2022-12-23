from .base_test import BaseMaterialQuantityTest
from ..models import Material, MaterialQuantity
from store.models import Store
from product.models import Product
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError
from ..serializers import MaterialQuantitySerializer
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class MaterialQuantityModelTest(BaseMaterialQuantityTest):
    def test_create_material_quantity(self):
        # Create 1st material
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        MaterialQuantity.objects.create(product = product, material = material, quantity = 10)
        self.assertEqual(MaterialQuantity.objects.count(), 1)

        # Create 2nd material
        product = Product.objects.get(pk = 2)
        material = Material.objects.get(pk = 2)
        MaterialQuantity.objects.create(product = product, material = material, quantity = 10)
        self.assertEqual(MaterialQuantity.objects.count(), 2)

    def test_material_product_pair_cannot_have_different_quantity(self):
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        MaterialQuantity.objects.create(product = product, material = material, quantity = 10)
        self.assertEqual(MaterialQuantity.objects.count(), 1)
        # unique_together = ['product', 'material']
        with self.assertRaises(IntegrityError):
            MaterialQuantity.objects.create(product = product, material = material, quantity = 10)

class MaterialQuantitySerializerTest(BaseMaterialQuantityTest):
    def test_serialize(self):
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        mq = MaterialQuantity.objects.create(product = product, material = material, quantity = 10)
        serializer = MaterialQuantitySerializer(mq)
        self.assertEqual(serializer.data['quantity'], 10)

    def test_deserialize(self):
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        data = {
            'product': product,
            'material': material,
            'quantity': 10
        }
        serializer = MaterialQuantitySerializer(data = data)
        self.assertTrue(serializer.is_valid())

    def test_cannot_save_duplicated_product_material(self):
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        data = {
            'product': product,
            'material': material,
            'quantity': 10
        }
        serializer = MaterialQuantitySerializer(data = data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        # unique_together = ['product', 'material']
        serializer = MaterialQuantitySerializer(data = data)
        self.assertFalse(serializer.is_valid())

    def test_cannot_save_negative_quantity(self):
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        data = {
            'product': product,
            'material': material,
            'quantity': -10
        }
        serializer = MaterialQuantitySerializer(data = data)
        self.assertFalse(serializer.is_valid())


class MaterialQuantityViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        store = Store.objects.create(name = 'store1', user = user)
        Product.objects.create(name = 'product1', store = store)
        Product.objects.create(name = 'product2', store = store)
        Material.objects.create(name = 'material1', price = 12.50, store = store)
        Material.objects.create(name = 'material2', price = 12.50, store = store)

    # Utils function for force authentication
    def force_authentication(self):
        user = User.objects.get(pk = 1)
        self.client.force_authenticate(user = user)

    # Utils function for creating a new material quantity
    def create_mq(self, product, material, quantity = 10):
        url = reverse('material_quantity-list')
        data = {
            'product': product,
            'material': material,
            'quantity': quantity
        }

        return self.client.post(url, data)

    def test_list_mq(self):
        # authenticate
        self.force_authentication()

        url = reverse("material_quantity-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_mq(self):
        # authenticate
        self.force_authentication()

        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        response = self.create_mq(product, material)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MaterialQuantity.objects.count(), 1)

    def test_update_mq(self):
        # authenticate
        self.force_authentication()

        # Create MQ
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        response = self.create_mq(product, material)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update MQ
        url = reverse("material_quantity-detail", args = (1, ))
        data = {
            'product': product,
            'material': material,
            'quantity': 50
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MaterialQuantity.objects.get().quantity, 50)

    def test_partial_update_mq(self):
        # authenticate
        self.force_authentication()

        # Create MQ
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        response = self.create_mq(product, material)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Partial update MQ
        url = reverse("material_quantity-detail", args = (1, ))
        data = {
            'quantity': 50
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MaterialQuantity.objects.get().quantity, 50)
        
    def test_retrieve_mq(self):
        # authenticate
        self.force_authentication()

        # Create MQ
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        response = self.create_mq(product, material)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Retrieve MQ
        url = reverse("material_quantity-detail", args = (1, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_mq(self):
        # authenticate
        self.force_authentication()

        # Create MQ
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)
        response = self.create_mq(product, material)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Delete MQ
        url = reverse("material_quantity-detail", args = (1, ))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MaterialQuantity.objects.count(), 0)
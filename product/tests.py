from django.test import TestCase
from store.models import Store
from django.contrib.auth import get_user_model
from .models import Product
from django.db import IntegrityError
from .serializers import ProductSerializer
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class ProductModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username = 'admin', password = 'password')
        Store.objects.create(name = 'store1', user = user)

    def test_create_product(self):
        store = Store.objects.get(pk = 1)
        Product.objects.create(name = 'product1', store = store)
        self.assertEqual(Product.objects.count(), 1)
        Product.objects.create(name = 'product2', store = store)
        self.assertEqual(Product.objects.count(), 2)

    def test_cannot_create_duplicated_product_in_same_store(self):
        store = Store.objects.get(pk = 1)
        Product.objects.create(name = 'product1', store = store)
        self.assertEqual(Product.objects.count(), 1)
        with self.assertRaises(IntegrityError):
            Product.objects.create(name = 'product1', store = store)

class ProductSerializerTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username = 'admin', password = 'password')
        Store.objects.create(name = 'store1', user = user)

    def test_serialize(self):
        store = Store.objects.get(pk = 1)
        product = Product.objects.create(name = 'product1', store = store)
        serializer = ProductSerializer(product)
        self.assertEqual(serializer.data['name'], 'product1')

    def test_deserialize(self):
        store = Store.objects.get(pk = 1)
        serializer = ProductSerializer(data = {'name': 'product1', 'store': store})
        self.assertTrue(serializer.is_valid())

    def test_cannot_create_same_product_in_same_store(self):
        store = Store.objects.get(pk = 1)
        serializer = ProductSerializer(data = {'name': 'product1', 'store': store})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        serializer = ProductSerializer(data = {'name': 'product1', 'store': store})
        self.assertFalse(serializer.is_valid())

class ProductViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = 'admin', password = 'password')
        Store.objects.create(name = 'store1', user = user)

    # Utils function for creating a new product
    def create_product(self, name, store):
        url = reverse('product-list')
        data = {
            'name': name,
            'store': store,
        }

        return self.client.post(url, data)

    def test_list_product(self):
        url = reverse('product-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product(self):
        name = 'product1'
        store = Store.objects.get(pk = 1)

        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

        name = 'product2'
        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_retrieve_product(self):
        # Create Product
        name = 'product1'
        store = Store.objects.get(pk = 1)

        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve Product
        url = reverse('product-detail', args = (1, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_product(self):
        # Create Product
        name = 'product1'
        store = Store.objects.get(pk = 1)

        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update Product
        data = {'name': 'new_product', 'store': store}
        url = reverse('product-detail', args = (1, ))
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk = 1).name, 'new_product')
    
    def test_partial_update_product(self):
        # Create Product
        name = 'product1'
        store = Store.objects.get(pk = 1)

        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Partial update Product
        data = {'name': 'new_product'}
        url = reverse('product-detail', args = (1, ))
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(pk = 1).name, 'new_product')

    def test_delete_product(self):
        # Create Product
        name = 'product1'
        store = Store.objects.get(pk = 1)

        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Delete Product
        url = reverse('product-detail', args = (1, ))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
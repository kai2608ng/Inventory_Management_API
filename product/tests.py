from django.test import TestCase
from store.models import Store
from django.contrib.auth import get_user_model
from .models import Product
from django.db import IntegrityError
from .serializers import ProductSerializer
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from material.models import MaterialQuantity, Material

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
        serializer = ProductSerializer(data = {'name': 'product1'})
        self.assertTrue(serializer.is_valid())

class ProductViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = 'admin', password = 'password')
        Store.objects.create(name = 'store1', user = user)

    # Utils function for force authentication
    def force_authentication(self, user = None):
        if not user:
            user = User.objects.get(pk = 1)
        self.client.force_authenticate(user = user)

    # Utils function for creating a new product
    def create_product(self, name, store):
        # authentication
        self.force_authentication()

        url = reverse('product-list')
        data = {
            'name': name,
        }

        return self.client.post(url, data)

    def test_list_product(self):
        # authentication
        self.force_authentication()

        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product(self):
        # authentication
        self.force_authentication()

        # Create 1st product
        name = 'product1'
        store = Store.objects.get(pk = 1)
        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

        # Create 2nd product
        name = 'product2'
        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_retrieve_product(self):
        # authentication
        self.force_authentication()

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
        # authentication
        self.force_authentication()

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
        # authentication
        self.force_authentication()

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
        # authentication
        self.force_authentication()

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

    def test_duplicate_product_return_error_message(self):
        # authentication
        self.force_authentication()

        # Create Product
        name = 'product1'
        store = Store.objects.get(pk = 1)
        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create Product
        name = 'product1'
        store = Store.objects.get(pk = 1)
        response = self.create_product(name, store)
        self.assertIn("error_messages", response.content.decode())

    def test_show_user_their_own_product(self):
        # authentication
        self.force_authentication()

        # Create Product
        name = 'product1'
        store = Store.objects.get(pk = 1)
        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create Product
        name = 'product2'
        store = Store.objects.get(pk = 1)
        response = self.create_product(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create new user
        user = User.objects.create_user(username = "admin2", password = "password123")
        self.force_authentication(user)
        Store.objects.create(name = 'store2', user = user)
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertIn('[]', response.content.decode())

class ProductCapacityViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = 'admin', password = 'password')
        store = Store.objects.create(name = 'store1', user = user)
        product1 = Product.objects.create(name = 'product1', store = store)
        product2 = Product.objects.create(name = 'product2', store = store)
        material1 = Material.objects.create(name = 'material1', price = 12.50, store = store, max_capacity = 100, current_capacity = 100)
        material2 = Material.objects.create(name = 'material2', price = 12.50, store = store, max_capacity = 100, current_capacity = 51)
        material3 = Material.objects.create(name = 'material3', price = 12.50, store = store, max_capacity = 100, current_capacity = 49)
        MaterialQuantity.objects.create(product = product1, material = material1, quantity = 10)
        MaterialQuantity.objects.create(product = product1, material = material2, quantity = 6)
        MaterialQuantity.objects.create(product = product1, material = material3, quantity = 9)

    # Utils function for force authentication
    def force_authentication(self, user = None):
        if not user:
            user = User.objects.get(pk = 1)
        self.client.force_authenticate(user = user)

    def test_list_product_capacity(self):
        # authentication
        self.force_authentication()

        url = reverse('product-product_capacity')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("remaining_capacities", response.content.decode())

class SaleViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = 'admin', password = 'password')
        store = Store.objects.create(name = 'store1', user = user)
        product1 = Product.objects.create(name = 'product1', store = store)
        product2 = Product.objects.create(name = 'product2', store = store)
        material1 = Material.objects.create(name = 'material1', price = 12.50, store = store, max_capacity = 100, current_capacity = 100)
        material2 = Material.objects.create(name = 'material2', price = 12.50, store = store, max_capacity = 100, current_capacity = 51)
        material3 = Material.objects.create(name = 'material3', price = 12.50, store = store, max_capacity = 100, current_capacity = 49)
        MaterialQuantity.objects.create(product = product1, material = material1, quantity = 10)
        MaterialQuantity.objects.create(product = product1, material = material2, quantity = 6)
        MaterialQuantity.objects.create(product = product1, material = material3, quantity = 9)

    # Utils function for force authentication
    def force_authentication(self, user = None):
        if not user:
            user = User.objects.get(pk = 1)
        self.client.force_authenticate(user = user)

    def test_create_sale(self):
        # authentication
        self.force_authentication()

        url = reverse('product-sale')
        data = {
            'sale': [
                {
                    'product': 1,
                    'quantity': 5,
                },{
                    'product': 2,
                    'quantity': 3
                }
            ]
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.content.decode())
        
    def test_create_sale_and_update_material_current_capacity(self):
        # authentication
        self.force_authentication()

        url = reverse('product-sale')
        data = {
            'sale': [
                {
                    'product': 1,
                    'quantity': 5,
                },{
                    'product': 2,
                    'quantity': 3
                }
            ]
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        material1 = Material.objects.get(pk = 1)
        material2 = Material.objects.get(pk = 2)
        material3 = Material.objects.get(pk = 3)
        self.assertEqual(material1.current_capacity, 50)
        self.assertEqual(material2.current_capacity, 21)
        self.assertEqual(material3.current_capacity, 4)
        
    def test_create_sale_with_invalid_quantity(self):
        # authentication
        self.force_authentication()

        url = reverse('product-sale')
        data = {
            'sale': [
                {
                    'product': 1,
                    'quantity': 15,
                },{
                    'product': 2,
                    'quantity': 3
                }
            ]
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("error_messages", response.content.decode())
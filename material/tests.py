from django.test import TestCase
from .models import Material, MaterialQuantity
from store.models import Store
from product.models import Product
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import IntegrityError
from .serializers import MaterialSerializer, MaterialQuantitySerializer
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class MaterialModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        Store.objects.create(name = 'store1', user = user)

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

class MaterialQuantityModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        store = Store.objects.create(name = 'store1', user = user)
        Product.objects.create(name = 'product1', store = store)
        Product.objects.create(name = 'product2', store = store)
        Material.objects.create(name = 'material1', price = 12.50, store = store)
        Material.objects.create(name = 'material2', price = 12.50, store = store)

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

class MaterialSerializerTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        Store.objects.create(name = 'store1', user = user)

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

    def test_cannot_create_duplicated_material_in_same_store(self):
        store = Store.objects.get(pk = 1)
        data = {
            'name': 'material1',
            'price': 12.50,
            'store': store
        }
        serializer = MaterialSerializer(data = data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        # unique_together = ['name', 'store']
        serializer = MaterialSerializer(data = data)
        self.assertFalse(serializer.is_valid())

class MaterialQuantitySerializerTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        store = Store.objects.create(name = 'store1', user = user)
        Product.objects.create(name = 'product1', store = store)
        Product.objects.create(name = 'product2', store = store)
        Material.objects.create(name = 'material1', price = 12.50, store = store)
        Material.objects.create(name = 'material2', price = 12.50, store = store)

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

class MaterialViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        Store.objects.create(name = 'store1', user = user)

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
        url = reverse('material-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_material(self):  
        name = "material1"
        store = Store.objects.get(pk = 1)
        
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)

    def test_retrive_material(self):
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
        # Create material
        name = "material1"
        store = Store.objects.get(pk = 1)
        
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update material
        url = reverse('material-detail', args = (1, ))
        name = "new_material"
        data = {
            'name': name,
            'price': 12.50,
            'store': store,
            'max_capacity': 100,
            'current_capacity': 100
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Material.objects.get(pk = 1).name, 'new_material')

    def test_partial_update_material(self):
        # Create material
        name = "material1"
        store = Store.objects.get(pk = 1)
        
        response = self.create_material(name, store)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Partial update material
        url = reverse('material-detail', args = (1, ))
        name = "new_material"
        data = {
            'name': name,
            'max_capacity': 100,
            'current_capacity': 100
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Material.objects.get(pk = 1).name, 'new_material')

    def test_delete_material(self):
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

class MaterialQuantityViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        store = Store.objects.create(name = 'store1', user = user)
        Product.objects.create(name = 'product1', store = store)
        Product.objects.create(name = 'product2', store = store)
        Material.objects.create(name = 'material1', price = 12.50, store = store)
        Material.objects.create(name = 'material2', price = 12.50, store = store)

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
        url = reverse("material_quantity-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_mq(self):
        product = Product.objects.get(pk = 1)
        material = Material.objects.get(pk = 1)

        response = self.create_mq(product, material)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MaterialQuantity.objects.count(), 1)

    def test_update_mq(self):
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
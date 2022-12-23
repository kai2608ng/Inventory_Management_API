from ..models import Material
from store.models import Store
from product.models import Product
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()

class BaseMaterialTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        Store.objects.create(name = 'store1', user = user)

class BaseMaterialQuantityTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        store = Store.objects.create(name = 'store1', user = user)
        Product.objects.create(name = 'product1', store = store)
        Product.objects.create(name = 'product2', store = store)
        Material.objects.create(name = 'material1', price = 12.50, store = store)
        Material.objects.create(name = 'material2', price = 12.50, store = store)

class BaseRestockTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        store = Store.objects.create(name = 'store1', user = user)
        Product.objects.create(name = 'product1', store = store)
        Product.objects.create(name = 'product2', store = store)
        Material.objects.create(name = 'material1', price = 12.50, store = store, max_capacity = 100, current_capacity = 100)
        Material.objects.create(name = 'material2', price = 12.50, store = store, max_capacity = 100, current_capacity = 49)
        Material.objects.create(name = 'material3', price = 12.50, store = store, max_capacity = 100, current_capacity = 48)


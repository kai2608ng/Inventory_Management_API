from .base_test import BaseRestockTest
from ..models import Material
from store.models import Store
from product.models import Product
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()

class InventoryViewTest(BaseRestockTest):
    def setUp(self):
        user = User.objects.create_user(username = "admin", password = "password123")
        store = Store.objects.create(name = 'store1', user = user)
        Product.objects.create(name = 'product1', store = store)
        Product.objects.create(name = 'product2', store = store)
        Material.objects.create(name = 'material1', price = 12.50, store = store, max_capacity = 100, current_capacity = 100)
        Material.objects.create(name = 'material2', price = 12.50, store = store, max_capacity = 100, current_capacity = 51)
        Material.objects.create(name = 'material3', price = 12.50, store = store, max_capacity = 100, current_capacity = 49)

    # Utils function for force authentication
    def force_authentication(self, user = None):
        if not user:
            user = User.objects.get(pk = 1)
        self.client.force_authenticate(user = user)

    def test_list_inventory(self):
        # authentication
        self.force_authentication()

        url = reverse('material-inventory')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("percentage_of_capacity", response.content.decode())
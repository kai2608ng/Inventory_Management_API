from .base_test import BaseRestockTest
from ..models import Material
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import F
from ..serializers import RestockSerializer, MaterialsSerializer
from rest_framework import status

User = get_user_model()
class MaterialsSerializerTest(BaseRestockTest):
    def test_serializer(self):
        restock_material = Material.objects.annotate(quantity = F('max_capacity') - F('current_capacity')).filter(quantity__gt = 0)
        serializer = MaterialsSerializer(restock_material.values('id', 'quantity'), many = True)
        self.assertEqual(len(serializer.data), 2)

    def test_deserialize(self):
        data = {'id': 2, 'quantity': 10}
        serializer = MaterialsSerializer(data = data)
        self.assertTrue(serializer.is_valid())

    def test_multiple_item_to_deserialize(self):
        data = [
            {
                'id': 2,
                'quantity': 5,
            },{
                'id': 3,
                'quantity': 10,
            }
        ]
        serializer = MaterialsSerializer(data = data, many = True)
        self.assertTrue(serializer.is_valid())

    def test_serializer_save_update_material_quantity(self):
        data = [
            {
                'id': 2,
                'quantity': 5,
            },{
                'id': 3,
                'quantity': 10,
            }
        ]
        serializer = MaterialsSerializer(data = data, many = True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        material1 = Material.objects.get(pk = 2)
        material2 = Material.objects.get(pk = 3)    
        self.assertTrue(material1.current_capacity, 54)
        self.assertTrue(material2.current_capacity, 58)

class RestockSerializerTest(BaseRestockTest):
    def test_deserialize(self):
        data = {
            'materials': [
                {
                    'id': 2,
                    'quantity': 5,
                },{
                    'id': 3,
                    'quantity': 10,
                }
            ],
            'total_price': 50
        }
        serializer = RestockSerializer(data = data)
        self.assertTrue(serializer.is_valid())
    
    def test_deserialize_update_material_current_quantity(self):
        data = {
            'materials': [
                {
                    'id': 2,
                    'quantity': 5,
                },{
                    'id': 3,
                    'quantity': 10,
                }
            ],
            'total_price': 50
        }
        serializer = RestockSerializer(data = data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        material1 = Material.objects.get(pk = 2)
        material2 = Material.objects.get(pk = 3)
        self.assertTrue(material1.current_capacity, 54)
        self.assertTrue(material2.current_capacity, 58)

class RestockViewTest(BaseRestockTest):
    # Utils function for force authentication
    def force_authentication(self, user = None):
        if not user:
            user = User.objects.get(pk = 1)
        self.client.force_authenticate(user = user)

    def test_list_restock(self):
        # authentication
        self.force_authentication()

        url = reverse('material-restock')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode()
        self.assertIn("materials", content)
        self.assertIn("total_price", content)

    def test_create_restock(self):
        # authentication
        self.force_authentication()

        url = reverse('material-restock')
        data = {
            'materials': [
                {
                    'id': 2,
                    'quantity': 15,
                },
                {
                    'id': 3,
                    'quantity': 20,
                }
            ],
            'total_price': 100.0
        }
        response = self.client.post(url, data)
        self.assertTrue(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Restock successfully", response.content.decode())
        material2 = Material.objects.get(pk = 2)
        material3 = Material.objects.get(pk = 3)
        self.assertEqual(material2.current_capacity, 64)
        self.assertEqual(material3.current_capacity, 68)

    def test_invalid_quantity_restock(self):
        # authentication
        self.force_authentication()

        url = reverse('material-restock')
        data = {
            'materials': [
                {
                    'id': 2,
                    'quantity': 500
                }
            ]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("error_messages", response.content.decode())

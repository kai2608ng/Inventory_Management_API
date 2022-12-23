from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import Product
from .serializers import ProductSerializer
from store.models import Store
from material.models import MaterialQuantity, Material
import json

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Only using user's own products
    def get_queryset(self):
        store = Store.objects.get(user = self.request.user)
        return Product.objects.filter(store = store)

    def create(self, request):
        store = Store.objects.get(user = request.user)
        name = request.data.get('name')

        # Check is the product within the store
        if Product.objects.filter(store = store, name = name).exists():
            return Response({"error_messages": "Product existed!"})

        serializer = self.get_serializer(data = {'name': name})
        if serializer.is_valid():
            serializer.save(store = store)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors)

    @action(detail = False, methods = ['get'], url_path = "product-capacity", url_name = "product_capacity")
    def product_capacity(self, request):
        remaining_capacities = []

        products = self.get_queryset()
        for product in products:
            remaining_capacity = {'product': product.id}
            min_quantity = 99999

            # Find the minimum quantity of the product that can be produced by the material
            for material in product.material_entries.all():
                mq = MaterialQuantity.objects.get(material = material, product = product)
                temp = material.current_capacity // mq.quantity
                # If there is one material that causes the product cannot be produced
                if temp == 0:
                    min_quantity = 0
                    break
                
                # If the current material can only produce a smaller number 
                # of product than other materials
                # Then the number of product can be produced must 
                # be less than or equal to temp
                if temp < min_quantity:
                    min_quantity = temp

            remaining_capacity['quantity'] = min_quantity if min_quantity != 99999 else 0
            remaining_capacities.append(remaining_capacity)
                
        return Response({"remaining_capacities": remaining_capacities})

    @action(detail = False, methods = ["post"])
    def sale(self, request):
        sales = [json.loads(sale.replace('\'', '\"')) for sale in request.data.getlist('sale')]
        track_material_quantity = {}

        for sale in sales:
            product = sale['product']
            quantity = sale['quantity']
            materials = Product.objects.get(pk = product).material_entries.all()
            for material in materials:
                mq = MaterialQuantity.objects.get(material = material, product = product)
                
                ## Check is it able to sale
                # If current capacity is less than the required quantity 
                # Response an error message
                if material.current_capacity - (mq.quantity * quantity) < 0:
                    return Response({"error_messages": "Please enter a valid sale data"})

                # Initialize the material to be tracked
                if material not in track_material_quantity:
                    track_material_quantity[material.pk] = 0
                # Track the quantity for each material that will be deducted later
                track_material_quantity[material.pk] += mq.quantity * quantity

        ## Product sold successfully and have to deduct the material that have been sold
        for material_id in track_material_quantity:
            m = Material.objects.get(pk = material_id)
            m.current_capacity -= track_material_quantity[material_id]
            m.save()

        return Response({"message": "Sale Successfully"})



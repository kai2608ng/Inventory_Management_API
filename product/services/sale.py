from rest_framework.response import Response

from product.models import Product
from material.models import Material, MaterialQuantity

def process_sales(sales):
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

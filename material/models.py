from django.db import models
from store.models import Store
from product.models import Product

class Material(models.Model):
    class Meta:
        db_table = "material"
        unique_together = ['name', 'store']

    def __str__(self):
        return self.name

    name = models.CharField(max_length = 40)   
    store = models.ForeignKey(Store, on_delete = models.CASCADE, related_name = "material_entries")
    price = models.DecimalField(max_digits = 20, decimal_places = 2)
    max_capacity = models.PositiveSmallIntegerField(default = 0)
    current_capacity = models.PositiveSmallIntegerField(default = 0)
    product = models.ManyToManyField(Product, through = "MaterialQuantity", related_name = "material_entries")

class MaterialQuantity(models.Model):
    class Meta:
        db_table = "material_quantity"
        unique_together = ['product', 'material']

    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = "product_material_quantity")
    material = models.ForeignKey(Material, on_delete = models.CASCADE, related_name = "material_material_quantity")
    quantity = models.PositiveSmallIntegerField(default = 0)

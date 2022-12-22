from django.db import models
from store.models import Store

class Product(models.Model):
    class Meta:
        db_table = "product"
        unique_together = ['name', 'store']

    name = models.CharField(max_length = 40)
    store = models.ForeignKey(Store, on_delete = models.CASCADE, related_name = "product_entries")

    def __str__(self):
        return self.name
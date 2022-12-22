from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Store(models.Model):
    class Meta:
        db_table = "store"

    name = models.CharField(max_length = 40)
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = "store_entries")

    def __str__(self):
        return self.name
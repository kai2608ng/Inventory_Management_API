from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Meta:
        db_table = "user"
        managed = False

    def __str__(self):
        return self.username
from django.contrib import admin
from .models import Material, MaterialQuantity

class MaterialAdmin(admin.ModelAdmin):
    pass

class MaterialQuantityAdmin(admin.ModelAdmin):
    pass

# Register your models here.
admin.site.register(Material, MaterialAdmin)
admin.site.register(MaterialQuantity, MaterialQuantityAdmin)
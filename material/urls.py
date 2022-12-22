from rest_framework.routers import SimpleRouter
from .models import Material, MaterialQuantity
from .views import MaterialViewSet, MaterialQuantityViewSet

router = SimpleRouter()
router.register(r'material', MaterialViewSet, basename = "material")
router.register(r'material-quantity', MaterialQuantityViewSet, basename = "material_quantity")

urlpatterns = router.urls
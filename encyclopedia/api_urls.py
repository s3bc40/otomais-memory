from rest_framework.routers import DefaultRouter

from .api_views import EquipmentViewSet, ItemTypeViewSet

router = DefaultRouter()
router.register("equipment", EquipmentViewSet, basename="equipment")
router.register("item-types", ItemTypeViewSet, basename="item-type")

urlpatterns = router.urls

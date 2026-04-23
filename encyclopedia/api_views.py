from rest_framework import viewsets

from .models import Equipment, ItemType, Set
from .serializers import (
    EquipmentDetailSerializer,
    EquipmentListSerializer,
    ItemTypeSerializer,
    SetDetailSerializer,
    SetListSerializer,
)


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Equipment.objects.select_related("item_type")
        .prefetch_related("effects")
        .order_by("level", "name")
    )
    lookup_field = "ankama_id"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EquipmentDetailSerializer
        return EquipmentListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if type_ := self.request.query_params.get("type"):
            qs = qs.filter(item_type__ankama_id=type_)
        if q := self.request.query_params.get("q"):
            qs = qs.filter(name__icontains=q)
        if (is_weapon := self.request.query_params.get("is_weapon")) is not None:
            qs = qs.filter(is_weapon=is_weapon.lower() in ("true", "1"))
        return qs


class ItemTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ItemType.objects.order_by("name")
    serializer_class = ItemTypeSerializer
    lookup_field = "ankama_id"
    pagination_class = None


class SetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Set.objects.prefetch_related("effects").order_by("level", "name")
    lookup_field = "ankama_id"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SetDetailSerializer
        return SetListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if level := self.request.query_params.get("level"):
            qs = qs.filter(level=level)
        if q := self.request.query_params.get("q"):
            qs = qs.filter(name__icontains=q)
        if (min_level := self.request.query_params.get("min_level")) is not None:
            qs = qs.filter(level__gte=int(min_level))
        if (max_level := self.request.query_params.get("max_level")) is not None:
            qs = qs.filter(level__lte=int(max_level))
        return qs

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
    queryset = Equipment.objects.select_related("item_type").order_by("level", "name")
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
        return qs

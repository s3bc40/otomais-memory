from rest_framework import serializers

from .models import Equipment, ItemType


class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemType
        fields = ("ankama_id", "name", "slug")


class EquipmentListSerializer(serializers.ModelSerializer):
    item_type = ItemTypeSerializer(read_only=True)

    class Meta:
        model = Equipment
        fields = ("ankama_id", "name", "level", "item_type", "image_icon_url")


class EquipmentDetailSerializer(serializers.ModelSerializer):
    item_type = ItemTypeSerializer(read_only=True)

    class Meta:
        model = Equipment
        fields = (
            "ankama_id",
            "name",
            "slug",
            "level",
            "item_type",
            "image_sd_url",
            "description",
        )

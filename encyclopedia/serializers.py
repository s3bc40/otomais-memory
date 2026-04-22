from rest_framework import serializers

from .models import Equipment, ItemType, Set, SetEffect


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


class SetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Set
        fields = (
            "ankama_id",
            "name",
            "slug",
            "level",
            "items_count",
            "contains_cosmetics",
            "contains_cosmetics_only",
        )


class SetEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetEffect
        fields = (
            "pieces_count",
            "effect_type_id",
            "effect_type_name",
            "effect_type_is_active",
            "effect_type_is_meta",
            "int_minimum",
            "int_maximum",
            "ignore_int_min",
            "ignore_int_max",
            "formatted",
        )


class SetDetailSerializer(serializers.ModelSerializer):
    effects = SetEffectSerializer(
        many=True,
        read_only=True,
        source="effects.all",
    )

    class Meta:
        model = Set
        fields = (
            "ankama_id",
            "name",
            "slug",
            "level",
            "items_count",
            "contains_cosmetics",
            "contains_cosmetics_only",
            "equipment_ids",
            "effects",
        )

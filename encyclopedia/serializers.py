from rest_framework import serializers

from .models import Equipment, EquipmentEffect, ItemType, Set, SetEffect


class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemType
        fields = ("ankama_id", "name", "slug")


class EquipmentListSerializer(serializers.ModelSerializer):
    item_type = ItemTypeSerializer(read_only=True)
    effects = serializers.SerializerMethodField()

    def get_effects(self, obj: Equipment) -> list[str]:
        return [e.formatted for e in obj.effects.all()]

    class Meta:
        model = Equipment
        fields = (
            "ankama_id",
            "name",
            "level",
            "item_type",
            "image_icon_url",
            "is_weapon",
            "pods",
            "parent_set_name",
            "effects",
        )


class EquipmentEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentEffect
        fields = (
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


class EquipmentDetailSerializer(serializers.ModelSerializer):
    item_type = ItemTypeSerializer(read_only=True)
    effects = EquipmentEffectSerializer(
        many=True,
        read_only=True,
        source="effects.all",
    )

    class Meta:
        model = Equipment
        fields = (
            "ankama_id",
            "name",
            "slug",
            "level",
            "item_type",
            "image_icon_url",
            "image_sd_url",
            "image_hq_url",
            "image_hd_url",
            "description",
            "pods",
            "is_weapon",
            "critical_hit_probability",
            "critical_hit_bonus",
            "max_cast_per_turn",
            "ap_cost",
            "range_min",
            "range_max",
            "parent_set_id",
            "parent_set_name",
            "recipe",
            "conditions",
            "effects",
        )


class SetListSerializer(serializers.ModelSerializer):
    effects_by_pieces = serializers.SerializerMethodField()

    def get_effects_by_pieces(self, obj: Set) -> dict[int, list[str]]:
        grouped: dict[int, list[str]] = {}
        for effect in obj.effects.all():
            grouped.setdefault(effect.pieces_count, []).append(effect.formatted)
        return grouped

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
            "effects_by_pieces",
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
    equipment_list = serializers.SerializerMethodField()

    def get_equipment_list(self, obj: Set) -> list[dict]:
        items = (
            Equipment.objects.filter(ankama_id__in=obj.equipment_ids or [])
            .select_related("item_type")
            .prefetch_related("effects")
            .order_by("level", "name")
        )
        return EquipmentListSerializer(items, many=True).data

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
            "equipment_list",
        )

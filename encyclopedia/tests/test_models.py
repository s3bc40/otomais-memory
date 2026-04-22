import pytest
from django.db import IntegrityError

from encyclopedia.models import Equipment, EquipmentEffect, ItemType


@pytest.mark.django_db
class TestEquipment:
    def test_should_persist_when_created_with_required_fields_only(
        self, item_type: ItemType
    ) -> None:
        eq = Equipment.objects.create(
            ankama_id=200,
            name="Test Item",
            level=5,
            item_type=item_type,
        )
        assert eq.pk is not None
        assert eq.name == "Test Item"
        assert eq.level == 5

    def test_should_store_all_fields_when_all_optional_fields_provided(
        self, item_type: ItemType
    ) -> None:
        eq = Equipment.objects.create(
            ankama_id=201,
            name="Full Item",
            level=10,
            item_type=item_type,
            slug="full-item",
            description="A full item.",
            pods=10,
            is_weapon=True,
            critical_hit_probability=5,
            critical_hit_bonus=8,
            max_cast_per_turn=3,
            ap_cost=4,
            range_min=1,
            range_max=3,
            parent_set_id=42,
            parent_set_name="Test Set",
            recipe=[{"ankama_id": 999, "quantity": 5}],
            conditions={"operator": "AND", "elements": []},
        )
        assert eq.pods == 10
        assert eq.is_weapon is True
        assert eq.parent_set_name == "Test Set"
        assert eq.recipe == [{"ankama_id": 999, "quantity": 5}]

    def test_should_include_level_in_str(self, equipment: Equipment) -> None:
        assert str(equipment) == "Amulette du Bouftou (lvl 1)"

    def test_should_raise_when_ankama_id_is_duplicate(
        self, item_type: ItemType, equipment: Equipment
    ) -> None:
        with pytest.raises(IntegrityError):
            Equipment.objects.create(
                ankama_id=101,
                name="Duplicate",
                level=1,
                item_type=item_type,
            )


@pytest.mark.django_db
class TestEquipmentEffect:
    def test_should_link_to_equipment_via_fk(self, equipment: Equipment) -> None:
        effect = EquipmentEffect.objects.create(
            equipment=equipment,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="100 Vitalité",
        )
        assert effect.equipment == equipment
        assert equipment.effects.count() == 1

    def test_should_delete_effects_when_equipment_is_deleted(
        self, equipment: Equipment
    ) -> None:
        EquipmentEffect.objects.create(
            equipment=equipment,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="100 Vitalité",
        )
        equipment.delete()
        assert EquipmentEffect.objects.count() == 0

    def test_should_include_formatted_value_in_str(self, equipment: Equipment) -> None:
        effect = EquipmentEffect.objects.create(
            equipment=equipment,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="100 Vitalité",
        )
        assert str(effect) == "Vitalité (100 Vitalité)"

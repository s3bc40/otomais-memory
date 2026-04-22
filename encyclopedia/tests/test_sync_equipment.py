from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from encyclopedia.models import Equipment, EquipmentEffect, ItemType

HTTPX_PATCH = "encyclopedia.management.commands.sync_equipment.httpx.get"

FULL_ITEM = {
    "ankama_id": 1001,
    "name": "Amulette du Bouftou",
    "level": 1,
    "type": {"id": 1, "name": "Amulette"},
    "image_urls": {
        "icon": "https://example.com/icon.png",
        "sd": "https://example.com/sd.png",
        "hq": "",
        "hd": "",
    },
    "description": "Une amulette de bouftou.",
    "pods": 10,
    "is_weapon": False,
    "range": {"min": 1, "max": 3},
    "parent_set": {"id": 42, "name": "Set du Bouftou"},
    "recipe": [{"ankama_id": 999, "quantity": 5}],
    "conditions": {"operator": "AND", "elements": []},
    "effects": [
        {
            "type": {
                "id": 10,
                "name": "Vitalité",
                "is_active": False,
                "is_meta": False,
            },
            "int_minimum": 50,
            "int_maximum": 100,
            "ignore_int_min": False,
            "ignore_int_max": False,
            "formatted": "50 à 100 Vitalité",
        },
        {
            "type": {"id": 11, "name": "Force", "is_active": False, "is_meta": False},
            "int_minimum": 20,
            "int_maximum": 20,
            "ignore_int_min": False,
            "ignore_int_max": False,
            "formatted": "20 Force",
        },
    ],
}

MINIMAL_ITEM = {
    "ankama_id": 1002,
    "name": "Cape Simple",
    "level": 1,
    "type": {"id": 2, "name": "Cape"},
}


def _mock_response(items: list) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = {"items": items}
    return mock


def run_sync(items: list) -> None:
    with patch(HTTPX_PATCH, return_value=_mock_response(items)):
        call_command("sync_equipment", verbosity=0)


@pytest.mark.django_db
class TestSyncEquipmentCommand:
    def test_should_create_equipment_when_item_is_full(self) -> None:
        run_sync([FULL_ITEM])

        eq = Equipment.objects.get(ankama_id=1001)
        assert eq.name == "Amulette du Bouftou"
        assert eq.level == 1
        assert eq.pods == 10
        assert eq.parent_set_id == 42
        assert eq.parent_set_name == "Set du Bouftou"
        assert eq.image_icon_url == "https://example.com/icon.png"

    def test_should_create_effects_when_item_has_effects(self) -> None:
        run_sync([FULL_ITEM])

        eq = Equipment.objects.get(ankama_id=1001)
        assert eq.effects.count() == 2
        effect = eq.effects.get(effect_type_id=10)
        assert effect.effect_type_name == "Vitalité"
        assert effect.int_minimum == 50
        assert effect.int_maximum == 100
        assert effect.formatted == "50 à 100 Vitalité"

    def test_should_assign_correct_effect_count_per_item(self) -> None:
        run_sync([FULL_ITEM, MINIMAL_ITEM])

        assert Equipment.objects.get(ankama_id=1001).effects.count() == 2
        assert Equipment.objects.get(ankama_id=1002).effects.count() == 0

    def test_should_use_defaults_when_optional_fields_are_absent(self) -> None:
        run_sync([MINIMAL_ITEM])

        eq = Equipment.objects.get(ankama_id=1002)
        assert eq.pods is None
        assert eq.description == ""
        assert eq.recipe == []
        assert eq.conditions == {}
        assert eq.range_min is None
        assert eq.range_max is None
        assert eq.parent_set_id is None
        assert eq.parent_set_name == ""

    def test_should_create_item_type_when_not_in_db(self) -> None:
        assert ItemType.objects.count() == 0
        run_sync([FULL_ITEM, MINIMAL_ITEM])

        assert ItemType.objects.filter(name="Amulette").exists()
        assert ItemType.objects.filter(name="Cape").exists()

    def test_should_be_idempotent_when_run_twice(self) -> None:
        run_sync([FULL_ITEM, MINIMAL_ITEM])
        run_sync([FULL_ITEM, MINIMAL_ITEM])

        assert Equipment.objects.count() == 2
        assert EquipmentEffect.objects.count() == 2
        assert ItemType.objects.count() == 2

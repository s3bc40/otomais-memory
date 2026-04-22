from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from encyclopedia.models import Set, SetEffect

HTTPX_PATCH = "encyclopedia.management.commands.sync_sets.httpx.get"

FULL_SET = {
    "ankama_id": 2001,
    "name": "Set du Bouftou",
    "level": 10,
    "items": 3,
    "equipment_ids": [101, 102, 103],
    "contains_cosmetics": False,
    "contains_cosmetics_only": False,
    "effects": {
        "2": [
            {
                "type": {
                    "id": 10,
                    "name": "Vitalité",
                    "is_active": False,
                    "is_meta": False,
                },
                "int_minimum": 50,
                "int_maximum": 50,
                "ignore_int_min": False,
                "ignore_int_max": False,
                "formatted": "50 Vitalité",
            },
        ],
        "3": [
            {
                "type": {
                    "id": 11,
                    "name": "Force",
                    "is_active": False,
                    "is_meta": False,
                },
                "int_minimum": 30,
                "int_maximum": 30,
                "ignore_int_min": False,
                "ignore_int_max": False,
                "formatted": "30 Force",
            },
            {
                "type": {
                    "id": 12,
                    "name": "Agilité",
                    "is_active": False,
                    "is_meta": False,
                },
                "int_minimum": 20,
                "int_maximum": 20,
                "ignore_int_min": False,
                "ignore_int_max": False,
                "formatted": "20 Agilité",
            },
        ],
    },
}

MINIMAL_SET = {
    "ankama_id": 2002,
    "name": "Set Minimal",
    "level": 1,
    "items": 0,
    "equipment_ids": [],
    "contains_cosmetics": False,
    "effects": {},
}

NULL_EFFECT_LIST_SET = {
    "ankama_id": 2003,
    "name": "Set Null Effects",
    "level": 5,
    "items": 2,
    "equipment_ids": [201, 202],
    "contains_cosmetics": False,
    "effects": {"2": None},
}


def _mock_response(sets: list) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = {"sets": sets}
    return mock


def run_sync(sets: list) -> None:
    with patch(HTTPX_PATCH, return_value=_mock_response(sets)):
        call_command("sync_sets", verbosity=0)


@pytest.mark.django_db
class TestSyncSetsCommand:
    def test_should_create_set_when_data_is_full(self) -> None:
        run_sync([FULL_SET])

        s = Set.objects.get(ankama_id=2001)
        assert s.name == "Set du Bouftou"
        assert s.level == 10
        assert s.items_count == 3
        assert s.equipment_ids == [101, 102, 103]
        assert s.contains_cosmetics is False

    def test_should_create_effects_with_correct_pieces_count(self) -> None:
        run_sync([FULL_SET])

        s = Set.objects.get(ankama_id=2001)
        assert s.effects.get(pieces_count=2).effect_type_name == "Vitalité"
        assert s.effects.get(pieces_count=2).formatted == "50 Vitalité"

    def test_should_assign_correct_effect_count_per_set(self) -> None:
        run_sync([FULL_SET, MINIMAL_SET])

        assert Set.objects.get(ankama_id=2001).effects.count() == 3
        assert Set.objects.get(ankama_id=2002).effects.count() == 0

    def test_should_use_defaults_when_optional_fields_are_absent(self) -> None:
        run_sync([MINIMAL_SET])

        s = Set.objects.get(ankama_id=2002)
        assert s.items_count == 0
        assert s.equipment_ids == []
        assert s.contains_cosmetics is False

    def test_should_not_raise_when_effect_list_is_null(self) -> None:
        run_sync([NULL_EFFECT_LIST_SET])

        s = Set.objects.get(ankama_id=2003)
        assert s.effects.count() == 0

    def test_should_be_idempotent_when_run_twice(self) -> None:
        run_sync([FULL_SET, MINIMAL_SET])
        run_sync([FULL_SET, MINIMAL_SET])

        assert Set.objects.count() == 2
        assert SetEffect.objects.count() == 3

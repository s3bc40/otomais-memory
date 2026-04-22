import pytest
from rest_framework.test import APIClient

from encyclopedia.models import Equipment, EquipmentEffect, ItemType


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestEquipmentListEndpoint:
    def test_should_return_200_and_paginated_response_when_list_requested(
        self, api_client: APIClient, equipment: Equipment
    ) -> None:
        response = api_client.get("/api/equipment/")

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert data["count"] == 1

    def test_should_return_only_matching_items_when_q_param_provided(
        self, api_client: APIClient, item_type: ItemType
    ) -> None:
        Equipment.objects.create(
            ankama_id=201, name="Amulette Dorée", level=5, item_type=item_type
        )
        Equipment.objects.create(
            ankama_id=202, name="Cape Bleue", level=3, item_type=item_type
        )

        response = api_client.get("/api/equipment/", {"q": "amulette"})

        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Amulette Dorée"

    def test_should_return_only_matching_items_when_type_param_provided(
        self, api_client: APIClient, item_type: ItemType
    ) -> None:
        other_type = ItemType.objects.create(ankama_id=2, name="Cape", slug="cape")
        Equipment.objects.create(
            ankama_id=201, name="Amulette Test", level=5, item_type=item_type
        )
        Equipment.objects.create(
            ankama_id=202, name="Cape Test", level=3, item_type=other_type
        )

        response = api_client.get("/api/equipment/", {"type": item_type.ankama_id})

        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["ankama_id"] == 201

    def test_should_not_expose_effects_in_list_response(
        self, api_client: APIClient, equipment: Equipment
    ) -> None:
        EquipmentEffect.objects.create(
            equipment=equipment,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="50 Vitalité",
        )

        response = api_client.get("/api/equipment/")

        assert response.status_code == 200
        assert "effects" not in response.json()["results"][0]


@pytest.mark.django_db
class TestEquipmentDetailEndpoint:
    def test_should_return_200_with_correct_ankama_id_when_detail_requested(
        self, api_client: APIClient, equipment: Equipment
    ) -> None:
        response = api_client.get(f"/api/equipment/{equipment.ankama_id}/")

        assert response.status_code == 200
        assert response.json()["ankama_id"] == equipment.ankama_id

    def test_should_return_nested_effects_when_detail_requested(
        self, api_client: APIClient, equipment: Equipment
    ) -> None:
        EquipmentEffect.objects.create(
            equipment=equipment,
            effect_type_id=10,
            effect_type_name="Vitalité",
            int_minimum=50,
            int_maximum=100,
            formatted="50 à 100 Vitalité",
        )

        response = api_client.get(f"/api/equipment/{equipment.ankama_id}/")

        assert response.status_code == 200
        effects = response.json()["effects"]
        assert len(effects) == 1
        assert effects[0]["effect_type_id"] == 10
        assert effects[0]["effect_type_name"] == "Vitalité"
        assert effects[0]["int_minimum"] == 50
        assert effects[0]["formatted"] == "50 à 100 Vitalité"

    def test_should_return_404_when_equipment_does_not_exist(
        self, api_client: APIClient
    ) -> None:
        response = api_client.get("/api/equipment/99999/")

        assert response.status_code == 404

    def test_should_not_expose_effects_in_list_response(
        self, api_client: APIClient, equipment: Equipment
    ) -> None:
        EquipmentEffect.objects.create(
            equipment=equipment,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="50 Vitalité",
        )

        response = api_client.get("/api/equipment/")

        assert response.status_code == 200
        assert "effects" not in response.json()["results"][0]

    def test_should_expose_all_enriched_fields_when_detail_requested(
        self, api_client: APIClient, item_type: ItemType
    ) -> None:
        eq = Equipment.objects.create(
            ankama_id=300,
            name="Équipement Complet",
            level=50,
            item_type=item_type,
            slug="equipement-complet",
            description="Un équipement de test.",
            pods=20,
            is_weapon=True,
            critical_hit_probability=10,
            critical_hit_bonus=8,
            max_cast_per_turn=3,
            ap_cost=4,
            range_min=1,
            range_max=3,
            parent_set_id=42,
            parent_set_name="Set du Bouftou",
            recipe=[{"ankama_id": 999, "quantity": 5}],
            conditions={"operator": "AND", "elements": []},
        )

        response = api_client.get(f"/api/equipment/{eq.ankama_id}/")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "equipement-complet"
        assert data["description"] == "Un équipement de test."
        assert data["pods"] == 20
        assert data["is_weapon"] is True
        assert data["critical_hit_probability"] == 10
        assert data["critical_hit_bonus"] == 8
        assert data["max_cast_per_turn"] == 3
        assert data["ap_cost"] == 4
        assert data["range_min"] == 1
        assert data["range_max"] == 3
        assert data["parent_set_id"] == 42
        assert data["parent_set_name"] == "Set du Bouftou"
        assert data["recipe"] == [{"ankama_id": 999, "quantity": 5}]
        assert data["conditions"] == {"operator": "AND", "elements": []}
        assert "effects" in data

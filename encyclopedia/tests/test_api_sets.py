import pytest
from rest_framework.test import APIClient

from encyclopedia.models import Set, SetEffect


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestSetListEndpoint:
    def test_should_return_200_and_paginated_response_when_list_requested(
        self, api_client: APIClient, equipment_set: Set
    ) -> None:
        response = api_client.get("/api/sets/")

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert data["count"] == 1

    def test_should_return_only_matching_items_when_q_param_provided(
        self, api_client: APIClient, db: None
    ) -> None:
        Set.objects.create(ankama_id=1, name="Set du Bouftou", level=10)
        Set.objects.create(ankama_id=2, name="Tenue du Crâ", level=20)

        response = api_client.get("/api/sets/", {"q": "bouftou"})

        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Set du Bouftou"

    def test_should_return_only_matching_items_when_level_param_provided(
        self, api_client: APIClient, db: None
    ) -> None:
        Set.objects.create(ankama_id=1, name="Set du Bouftou", level=10)
        Set.objects.create(ankama_id=2, name="Tenue du Crâ", level=20)

        response = api_client.get("/api/sets/", {"level": 10})

        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Set du Bouftou"

    def test_should_not_expose_effects_or_equipment_ids_in_list_response(
        self, api_client: APIClient, equipment_set: Set
    ) -> None:
        SetEffect.objects.create(
            set=equipment_set,
            pieces_count=2,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="50 Vitalité",
        )

        response = api_client.get("/api/sets/")

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert "effects" not in result
        assert "equipment_ids" not in result


@pytest.mark.django_db
class TestSetDetailEndpoint:
    def test_should_return_200_with_correct_ankama_id_when_detail_requested(
        self, api_client: APIClient, equipment_set: Set
    ) -> None:
        response = api_client.get(f"/api/sets/{equipment_set.ankama_id}/")

        assert response.status_code == 200
        assert response.json()["ankama_id"] == equipment_set.ankama_id

    def test_should_return_nested_effects_with_pieces_count_when_detail_requested(
        self, api_client: APIClient, equipment_set: Set
    ) -> None:
        SetEffect.objects.create(
            set=equipment_set,
            pieces_count=2,
            effect_type_id=10,
            effect_type_name="Vitalité",
            int_minimum=50,
            int_maximum=50,
            formatted="50 Vitalité",
        )
        SetEffect.objects.create(
            set=equipment_set,
            pieces_count=3,
            effect_type_id=11,
            effect_type_name="Force",
            int_minimum=30,
            int_maximum=30,
            formatted="30 Force",
        )

        response = api_client.get(f"/api/sets/{equipment_set.ankama_id}/")

        assert response.status_code == 200
        effects = response.json()["effects"]
        assert len(effects) == 2
        assert effects[0]["pieces_count"] == 2
        assert effects[0]["effect_type_name"] == "Vitalité"
        assert effects[1]["pieces_count"] == 3
        assert effects[1]["effect_type_name"] == "Force"

    def test_should_return_404_when_set_does_not_exist(
        self, api_client: APIClient
    ) -> None:
        response = api_client.get("/api/sets/99999/")

        assert response.status_code == 404

    def test_should_expose_equipment_ids_and_nested_effects_in_detail_response(
        self, api_client: APIClient, equipment_set: Set
    ) -> None:
        SetEffect.objects.create(
            set=equipment_set,
            pieces_count=2,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="50 Vitalité",
        )

        response = api_client.get(f"/api/sets/{equipment_set.ankama_id}/")

        assert response.status_code == 200
        data = response.json()
        assert data["equipment_ids"] == [101, 102, 103]
        assert isinstance(data["effects"], list)
        assert len(data["effects"]) == 1
        assert data["effects"][0]["pieces_count"] == 2

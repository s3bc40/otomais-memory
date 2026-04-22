import pytest

from encyclopedia.models import Set, SetEffect


@pytest.mark.django_db
class TestSet:
    def test_should_persist_when_created_with_required_fields_only(self) -> None:
        s = Set.objects.create(ankama_id=1, name="Set du Bouftou", level=10)
        assert s.pk is not None
        assert s.name == "Set du Bouftou"
        assert s.level == 10

    def test_should_store_all_fields_when_all_optional_fields_provided(self) -> None:
        s = Set.objects.create(
            ankama_id=2,
            name="Set Complet",
            slug="set-complet",
            level=20,
            items_count=5,
            equipment_ids=[1, 2, 3, 4, 5],
            contains_cosmetics=True,
            contains_cosmetics_only=False,
        )
        assert s.items_count == 5
        assert s.equipment_ids == [1, 2, 3, 4, 5]
        assert s.contains_cosmetics is True
        assert s.contains_cosmetics_only is False

    def test_should_include_level_in_str(self, equipment_set: Set) -> None:
        assert str(equipment_set) == "Set du Bouftou (lv. 10)"

    def test_should_allow_duplicate_slugs(self) -> None:
        Set.objects.create(ankama_id=10, name="Set A", slug="same-slug", level=1)
        Set.objects.create(ankama_id=11, name="Set B", slug="same-slug", level=1)
        assert Set.objects.filter(slug="same-slug").count() == 2


@pytest.mark.django_db
class TestSetEffect:
    def test_should_link_to_set_via_fk(self, equipment_set: Set) -> None:
        effect = SetEffect.objects.create(
            set=equipment_set,
            pieces_count=2,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="50 Vitalité",
        )
        assert effect.set == equipment_set
        assert equipment_set.effects.count() == 1

    def test_should_delete_effects_when_set_is_deleted(
        self, equipment_set: Set
    ) -> None:
        SetEffect.objects.create(
            set=equipment_set,
            pieces_count=2,
            effect_type_id=1,
            effect_type_name="Vitalité",
            formatted="50 Vitalité",
        )
        equipment_set.delete()
        assert SetEffect.objects.count() == 0

    def test_should_include_pieces_count_and_formatted_in_str(
        self, equipment_set: Set
    ) -> None:
        effect = SetEffect.objects.create(
            set=equipment_set,
            pieces_count=3,
            effect_type_id=1,
            effect_type_name="Force",
            formatted="30 Force",
        )
        assert str(effect) == "Set du Bouftou — 3 pieces: 30 Force"

import pytest

from encyclopedia.models import Equipment, ItemType, Set


@pytest.fixture
def item_type(db) -> ItemType:
    """Create an item type for testing.

    Note: The `db` fixture is what grants database access to that fixture scope.
    """
    return ItemType.objects.create(ankama_id=1, name="Amulette", slug="amulette")


@pytest.fixture
def equipment(item_type: ItemType) -> Equipment:
    return Equipment.objects.create(
        ankama_id=101,
        name="Amulette du Bouftou",
        level=1,
        item_type=item_type,
    )


@pytest.fixture
def equipment_set(db) -> Set:
    return Set.objects.create(
        ankama_id=1,
        name="Set du Bouftou",
        slug="set-du-bouftou",
        level=10,
        items_count=3,
        equipment_ids=[101, 102, 103],
    )

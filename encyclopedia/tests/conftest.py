import pytest

from encyclopedia.models import Equipment, ItemType


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

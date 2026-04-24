import pytest
from rest_framework.test import APIClient

from encyclopedia.models import Equipment, EquipmentEffect, ItemType, Set, SetEffect


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def item_type(db) -> ItemType:
    return ItemType.objects.create(ankama_id=1, name="Amulette", slug="amulette")


@pytest.fixture
def populated_equipment(item_type: ItemType) -> list[Equipment]:
    """Create a batch of equipment with effects for realistic benchmarking."""
    items = []
    for i in range(50):
        eq = Equipment.objects.create(
            ankama_id=1000 + i,
            name=f"Equipment {i}",
            level=(i % 200) + 1,
            item_type=item_type,
            is_weapon=i % 3 == 0,
            pods=i * 2,
        )
        for j in range(3):
            EquipmentEffect.objects.create(
                equipment=eq,
                effect_type_id=j + 1,
                effect_type_name=f"Effect {j}",
                int_minimum=j * 10,
                int_maximum=j * 20,
                formatted=f"{j * 10} to {j * 20} Effect {j}",
            )
        items.append(eq)
    return items


@pytest.fixture
def populated_sets(db) -> list[Set]:
    """Create a batch of sets with effects for realistic benchmarking."""
    sets = []
    for i in range(20):
        s = Set.objects.create(
            ankama_id=2000 + i,
            name=f"Set {i}",
            slug=f"set-{i}",
            level=(i * 10) + 1,
            items_count=3 + (i % 4),
            equipment_ids=[1000 + i, 1001 + i, 1002 + i],
        )
        for pieces in range(2, 4):
            for j in range(2):
                SetEffect.objects.create(
                    set=s,
                    pieces_count=pieces,
                    effect_type_id=j + 1,
                    effect_type_name=f"Bonus {j}",
                    int_minimum=pieces * 10,
                    int_maximum=pieces * 10,
                    formatted=f"{pieces * 10} Bonus {j}",
                )
        sets.append(s)
    return sets


# -- Model benchmarks --


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_equipment_creation(benchmark, item_type: ItemType) -> None:
    """Benchmark creating an Equipment instance."""
    counter = 0

    @benchmark
    def _():
        nonlocal counter
        counter += 1
        Equipment.objects.create(
            ankama_id=5000 + counter,
            name=f"Bench Item {counter}",
            level=50,
            item_type=item_type,
        )


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_equipment_queryset_filter(
    benchmark, populated_equipment: list[Equipment]
) -> None:
    """Benchmark filtering equipment by weapon status."""

    @benchmark
    def _():
        list(Equipment.objects.filter(is_weapon=True).select_related("item_type"))


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_equipment_queryset_search(
    benchmark, populated_equipment: list[Equipment]
) -> None:
    """Benchmark name search across equipment."""

    @benchmark
    def _():
        list(Equipment.objects.filter(name__icontains="Equipment 1"))


# -- Serializer benchmarks --


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_equipment_list_serialization(
    benchmark, populated_equipment: list[Equipment]
) -> None:
    """Benchmark serializing a list of equipment."""
    from encyclopedia.serializers import EquipmentListSerializer

    qs = (
        Equipment.objects.select_related("item_type")
        .prefetch_related("effects")
        .order_by("level", "name")[:24]
    )

    @benchmark
    def _():
        items = list(qs)
        EquipmentListSerializer(items, many=True).data


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_set_list_serialization(benchmark, populated_sets: list[Set]) -> None:
    """Benchmark serializing a list of sets."""
    from encyclopedia.serializers import SetListSerializer

    qs = Set.objects.prefetch_related("effects").order_by("level", "name")[:24]

    @benchmark
    def _():
        items = list(qs)
        SetListSerializer(items, many=True).data


# -- API endpoint benchmarks --


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_api_equipment_list(
    benchmark, api_client: APIClient, populated_equipment: list[Equipment]
) -> None:
    """Benchmark the equipment list endpoint."""

    @benchmark
    def _():
        response = api_client.get("/api/equipment/")
        assert response.status_code == 200


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_api_equipment_list_filtered(
    benchmark, api_client: APIClient, populated_equipment: list[Equipment]
) -> None:
    """Benchmark the equipment list endpoint with search filter."""

    @benchmark
    def _():
        response = api_client.get("/api/equipment/", {"q": "Equipment 1"})
        assert response.status_code == 200


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_api_equipment_detail(
    benchmark, api_client: APIClient, populated_equipment: list[Equipment]
) -> None:
    """Benchmark the equipment detail endpoint."""

    @benchmark
    def _():
        response = api_client.get("/api/equipment/1000/")
        assert response.status_code == 200


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_api_sets_list(
    benchmark, api_client: APIClient, populated_sets: list[Set]
) -> None:
    """Benchmark the sets list endpoint."""

    @benchmark
    def _():
        response = api_client.get("/api/sets/")
        assert response.status_code == 200


@pytest.mark.benchmark
@pytest.mark.django_db
def test_bench_api_sets_list_filtered(
    benchmark, api_client: APIClient, populated_sets: list[Set]
) -> None:
    """Benchmark the sets list endpoint with level range filter."""

    @benchmark
    def _():
        response = api_client.get("/api/sets/", {"min_level": "50", "max_level": "150"})
        assert response.status_code == 200

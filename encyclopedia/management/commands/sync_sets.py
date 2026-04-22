import time

import httpx
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from encyclopedia.models import Set, SetEffect

ALL_URL = "https://api.dofusdu.de/dofus3/v1/fr/sets/all"


class Command(BaseCommand):
    help = "Sync all sets from the dofusdude API (single gzip request)"

    def handle(self, *args: object, **options: object) -> None:
        created = updated = errors = effects_total = 0

        t0 = time.perf_counter()
        resp = httpx.get(
            ALL_URL,
            headers={"Accept-Encoding": "gzip"},
            timeout=60,
        )
        resp.raise_for_status()
        items = resp.json().get("sets", [])
        t1 = time.perf_counter()
        self.stdout.write(f"Fetched {len(items)} sets, syncing…")

        with transaction.atomic():
            for item in items:
                try:
                    equipment_set, was_created = Set.objects.update_or_create(
                        ankama_id=item["ankama_id"],
                        defaults={
                            "name": item["name"],
                            "slug": slugify(item["name"]),
                            "level": item.get("level", 0),
                            "items_count": item.get("items", 0),
                            "equipment_ids": item.get("equipment_ids") or [],
                            "contains_cosmetics": item.get("contains_cosmetics", False),
                            "contains_cosmetics_only": item.get(
                                "contains_cosmetics_only", False
                            ),
                        },
                    )

                    equipment_set.effects.all().delete()
                    effects = [
                        SetEffect(
                            set=equipment_set,
                            pieces_count=int(pieces_count),
                            effect_type_id=e["type"]["id"],
                            effect_type_name=e["type"]["name"],
                            effect_type_is_active=e["type"].get("is_active", False),
                            effect_type_is_meta=e["type"].get("is_meta", False),
                            int_minimum=e.get("int_minimum", 0),
                            int_maximum=e.get("int_maximum", 0),
                            ignore_int_min=e.get("ignore_int_min", False),
                            ignore_int_max=e.get("ignore_int_max", False),
                            formatted=e.get("formatted", ""),
                        )
                        for pieces_count, effect_list in (
                            item.get("effects") or {}
                        ).items()
                        for e in (effect_list or [])
                    ]
                    SetEffect.objects.bulk_create(effects)
                    effects_total += len(effects)

                    if was_created:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    errors += 1
                    self.stderr.write(
                        f"Error on ankama_id={item.get('ankama_id')}: {e}"
                    )

        t2 = time.perf_counter()
        self.stdout.write(
            self.style.SUCCESS(
                f"Done — created: {created}, updated: {updated}, "
                f"effects: {effects_total}, errors: {errors}\n"
                f"  fetch: {t1 - t0:.2f}s | sync: {t2 - t1:.2f}s | total: {t2 - t0:.2f}s"
            )
        )

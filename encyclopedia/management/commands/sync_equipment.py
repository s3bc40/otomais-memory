import httpx
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from encyclopedia.models import Equipment, EquipmentEffect, ItemType

ALL_URL = "https://api.dofusdu.de/dofus3/v1/fr/items/equipment/all"


class Command(BaseCommand):
    help = "Sync all equipment from the dofusdude API (single gzip request)"

    def handle(self, *args: object, **options: object) -> None:
        created = updated = errors = effects_total = 0

        resp = httpx.get(
            ALL_URL,
            headers={"Accept-Encoding": "gzip"},
            timeout=60,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        self.stdout.write(f"Fetched {len(items)} items, syncing…")

        for item in items:
            try:
                type_data = item["type"]
                item_type, _ = ItemType.objects.get_or_create(
                    ankama_id=type_data["id"],
                    defaults={
                        "name": type_data["name"],
                        "slug": slugify(type_data["name"]),
                    },
                )

                image_urls = item.get("image_urls", {})
                range_data = item.get("range") or {}
                parent_set = item.get("parent_set") or {}

                equipment, was_created = Equipment.objects.update_or_create(
                    ankama_id=item["ankama_id"],
                    defaults={
                        "name": item["name"],
                        "slug": slugify(item["name"]),
                        "level": item["level"],
                        "item_type": item_type,
                        "image_icon_url": image_urls.get("icon", ""),
                        "image_sd_url": image_urls.get("sd", ""),
                        "image_hq_url": image_urls.get("hq", ""),
                        "image_hd_url": image_urls.get("hd", ""),
                        "description": item.get("description", ""),
                        "pods": item.get("pods"),
                        "is_weapon": item.get("is_weapon", False),
                        "critical_hit_probability": item.get(
                            "critical_hit_probability"
                        ),
                        "critical_hit_bonus": item.get("critical_hit_bonus"),
                        "max_cast_per_turn": item.get("max_cast_per_turn"),
                        "ap_cost": item.get("ap_cost"),
                        "range_min": range_data.get("min"),
                        "range_max": range_data.get("max"),
                        "parent_set_id": parent_set.get("id"),
                        "parent_set_name": parent_set.get("name", ""),
                        "recipe": item.get("recipe") or [],
                        "conditions": item.get("conditions") or {},
                    },
                )

                effects_data = item.get("effects") or []
                equipment.effects.all().delete()
                effects = [
                    EquipmentEffect(
                        equipment=equipment,
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
                    for e in effects_data
                ]
                EquipmentEffect.objects.bulk_create(effects)
                effects_total += len(effects)

                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
                self.stderr.write(f"Error on ankama_id={item.get('ankama_id')}: {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — created: {created}, updated: {updated}, "
                f"effects: {effects_total}, errors: {errors}"
            )
        )

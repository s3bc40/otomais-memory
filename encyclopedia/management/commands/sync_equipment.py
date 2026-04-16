import httpx
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from encyclopedia.models import Equipment, ItemType

ALL_URL = "https://api.dofusdu.de/dofus3/v1/fr/items/equipment/all"


class Command(BaseCommand):
    help = "Sync all equipment from the dofusdude API (single gzip request)"

    def handle(self, *args: object, **options: object) -> None:
        created = updated = errors = 0

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
                _, was_created = Equipment.objects.update_or_create(
                    ankama_id=item["ankama_id"],
                    defaults={
                        "name": item["name"],
                        "slug": slugify(item["name"]),
                        "level": item["level"],
                        "item_type": item_type,
                        "image_icon_url": image_urls.get("icon", ""),
                        "image_sd_url": image_urls.get("sd", ""),
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
                self.stderr.write(
                    f"Error on ankama_id={item.get('ankama_id')}: {e}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — created: {created}, updated: {updated}, errors: {errors}"
            )
        )

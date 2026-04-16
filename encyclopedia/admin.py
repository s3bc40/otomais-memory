from django.contrib import admin

from encyclopedia.models import Equipment, ItemType


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ["name", "level", "item_type"]
    list_filter = ["item_type"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

from django.contrib import admin

from encyclopedia.models import Equipment, EquipmentEffect, ItemType


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class EquipmentEffectInline(admin.TabularInline):
    model = EquipmentEffect
    extra = 0
    fields = ["effect_type_name", "int_minimum", "int_maximum", "formatted"]


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ["name", "level", "item_type", "is_weapon", "pods"]
    list_filter = ["item_type", "is_weapon"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [EquipmentEffectInline]


@admin.register(EquipmentEffect)
class EquipmentEffectAdmin(admin.ModelAdmin):
    list_display = [
        "equipment",
        "effect_type_name",
        "int_minimum",
        "int_maximum",
        "formatted",
    ]
    list_filter = ["effect_type_is_active", "effect_type_is_meta"]
    search_fields = ["effect_type_name", "equipment__name"]

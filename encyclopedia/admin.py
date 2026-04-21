from django.contrib import admin

from encyclopedia.models import Equipment, EquipmentEffect, ItemType


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class EquipmentEffectInline(admin.TabularInline):
    model = EquipmentEffect
    extra = 0
    readonly_fields = [
        "effect_type_name",
        "effect_type_is_active",
        "effect_type_is_meta",
        "int_minimum",
        "int_maximum",
        "formatted",
    ]
    fields = [
        "effect_type_name",
        "effect_type_is_active",
        "effect_type_is_meta",
        "int_minimum",
        "int_maximum",
        "formatted",
    ]


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "level",
        "item_type",
        "is_weapon",
        "pods",
        "ap_cost",
        "effect_count",
    ]
    list_filter = ["item_type", "is_weapon", "level"]
    search_fields = ["name", "parent_set_name"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["ankama_id", "effect_count"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "ankama_id",
                    "name",
                    "slug",
                    "level",
                    "item_type",
                    "description",
                ]
            },
        ),
        (
            "Images",
            {
                "fields": [
                    "image_icon_url",
                    "image_sd_url",
                    "image_hq_url",
                    "image_hd_url",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Weapon stats",
            {
                "fields": [
                    "is_weapon",
                    "ap_cost",
                    "range_min",
                    "range_max",
                    "critical_hit_probability",
                    "critical_hit_bonus",
                    "max_cast_per_turn",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Set & misc",
            {
                "fields": ["pods", "parent_set_id", "parent_set_name"],
                "classes": ["collapse"],
            },
        ),
        ("Data", {"fields": ["recipe", "conditions"], "classes": ["collapse"]}),
    ]
    inlines = [EquipmentEffectInline]

    @admin.display(description="Effects")
    def effect_count(self, obj: Equipment) -> int:
        return obj.effects.count()


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

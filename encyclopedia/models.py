from django.db import models


class ItemType(models.Model):
    ankama_id = models.IntegerField(unique=True, null=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "item type"
        verbose_name_plural = "item types"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Equipment(models.Model):
    ankama_id = models.IntegerField(unique=True, null=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, default="")
    level = models.PositiveSmallIntegerField()
    item_type = models.ForeignKey(
        ItemType,
        on_delete=models.PROTECT,
        related_name="equipment",
    )
    image_icon_url = models.URLField(blank=True)
    image_sd_url = models.URLField(blank=True)
    image_hq_url = models.URLField(blank=True)
    image_hd_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    pods = models.IntegerField(null=True, blank=True)
    is_weapon = models.BooleanField(default=False, null=True, blank=True)
    critical_hit_probability = models.IntegerField(null=True, blank=True)
    critical_hit_bonus = models.IntegerField(null=True, blank=True)
    max_cast_per_turn = models.IntegerField(null=True, blank=True)
    ap_cost = models.IntegerField(null=True, blank=True)
    range_min = models.IntegerField(null=True, blank=True)
    range_max = models.IntegerField(null=True, blank=True)
    parent_set_id = models.IntegerField(null=True, blank=True)
    parent_set_name = models.CharField(max_length=255, blank=True)
    recipe = models.JSONField(default=list, null=True, blank=True)
    conditions = models.JSONField(default=dict, null=True, blank=True)

    class Meta:
        verbose_name = "equipment"
        verbose_name_plural = "equipment"
        ordering = ["level", "name"]

    def __str__(self) -> str:
        return f"{self.name} (lvl {self.level})"


class EquipmentEffect(models.Model):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="effects",
    )
    effect_type_id = models.IntegerField()
    effect_type_name = models.CharField(max_length=255)
    effect_type_is_active = models.BooleanField(default=False)
    effect_type_is_meta = models.BooleanField(default=False)
    int_minimum = models.IntegerField(default=0)
    int_maximum = models.IntegerField(default=0)
    ignore_int_min = models.BooleanField(default=False)
    ignore_int_max = models.BooleanField(default=False)
    formatted = models.CharField(max_length=512, blank=True)

    class Meta:
        verbose_name = "equipment effect"
        verbose_name_plural = "equipment effects"

    def __str__(self) -> str:
        return f"{self.effect_type_name} ({self.formatted})"


class Set(models.Model):
    ankama_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, default="")
    level = models.IntegerField(default=0)
    items_count = models.IntegerField(default=0)
    equipment_ids = models.JSONField(default=list)
    contains_cosmetics = models.BooleanField(default=False)
    contains_cosmetics_only = models.BooleanField(default=False)

    class Meta:
        verbose_name = "set"
        verbose_name_plural = "sets"
        ordering = ["level", "name"]

    def __str__(self) -> str:
        return f"{self.name} (lv. {self.level})"


class SetEffect(models.Model):
    set = models.ForeignKey(
        Set,
        on_delete=models.CASCADE,
        related_name="effects",
    )
    pieces_count = models.IntegerField()
    effect_type_id = models.IntegerField()
    effect_type_name = models.CharField(max_length=255)
    effect_type_is_active = models.BooleanField(default=False)
    effect_type_is_meta = models.BooleanField(default=False)
    int_minimum = models.IntegerField(default=0)
    int_maximum = models.IntegerField(default=0)
    ignore_int_min = models.BooleanField(default=False)
    ignore_int_max = models.BooleanField(default=False)
    formatted = models.CharField(max_length=512, blank=True)

    class Meta:
        verbose_name = "set effect"
        verbose_name_plural = "set effects"
        ordering = ["pieces_count"]

    def __str__(self) -> str:
        return f"{self.set.name} — {self.pieces_count} pieces: {self.formatted}"

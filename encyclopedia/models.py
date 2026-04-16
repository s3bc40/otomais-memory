from django.db import models


class ItemType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "item type"
        verbose_name_plural = "item types"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    level = models.PositiveSmallIntegerField()
    item_type = models.ForeignKey(
        ItemType,
        on_delete=models.PROTECT,
        related_name="equipment",
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "equipment"
        verbose_name_plural = "equipment"
        ordering = ["level", "name"]

    def __str__(self) -> str:
        return f"{self.name} (lvl {self.level})"

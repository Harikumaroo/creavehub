"""
CraveHub — Categories App Models
"""

from django.db import models
from django.utils.text import slugify
from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True, db_index=True)
    image = models.URLField(max_length=500, blank=True, default="")
    icon = models.URLField(max_length=500, blank=True, default="")
    emoji = models.CharField(max_length=10, blank=True, default="")
    display_order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
        db_index=True,
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(
                fields=["is_active", "display_order"],
                name="idx_cat_active_order",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        qs = Category.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            qs = Category.objects.filter(slug=slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
        return slug
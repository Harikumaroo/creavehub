"""
CraveHub — Banners Models
"""

from django.db import models
from django.utils import timezone
from core.models import BaseModel


class BannerQuerySet(models.QuerySet):
    def active(self):
        today = timezone.now().date()
        return self.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )


class BannerManager(models.Manager):
    def get_queryset(self):
        return BannerQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class Banner(BaseModel):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, default="")
    image = models.URLField(max_length=500)
    redirect_url = models.URLField(max_length=500, blank=True, default="")
    priority = models.PositiveSmallIntegerField(default=100, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)

    objects = BannerManager()

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ["priority", "-created_at"]
        indexes = [
            models.Index(
                fields=["is_active", "start_date", "end_date", "priority"],
                name="idx_banner_active_priority",   # ← fixed, shortened
            )
        ]

    def __str__(self):
        return self.title

    @property
    def is_currently_active(self) -> bool:
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date
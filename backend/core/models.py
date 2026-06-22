"""
CraveHub Core Models
Abstract base models shared across all apps.
"""

import uuid
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.id)


class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def soft_delete(self):
        return self.update(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)


class SoftDeleteModel(BaseModel):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self) -> None:
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])


class AppSector(BaseModel):
    """
    A dynamic service tile displayed on the home screen.
    Managed via Django Admin so sectors can be added/removed/toggled
    without code changes.
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    emoji = models.CharField(max_length=10, default="🍽️")
    bg_gradient_start = models.CharField(
        max_length=9, default="#FFF0E6",
        help_text="CSS hex colour for gradient start",
    )
    bg_gradient_end = models.CharField(
        max_length=9, default="#FFE4CC",
        help_text="CSS hex colour for gradient end",
    )
    border_color = models.CharField(max_length=9, default="#F5C9A0")
    route = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Frontend route key, e.g. 'instamart', 'dining'. "
                  "Leave blank for 'coming soon'.",
    )
    display_order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "app_sectors"
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.emoji} {self.name}"
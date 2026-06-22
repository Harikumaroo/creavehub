"""
CraveHub — Categories Signals
Auto-invalidate Redis cache on any Category change.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Category
from .services import CategoryService


@receiver(post_save, sender=Category)
def invalidate_cache_on_save(sender, instance, **kwargs):
    CategoryService.invalidate_cache()


@receiver(post_delete, sender=Category)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    CategoryService.invalidate_cache()
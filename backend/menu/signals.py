"""
CraveHub — Menu Signals
Invalidate per-restaurant menu cache on any item or category change.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import MenuCategory, MenuItem
from .services import MenuService


@receiver(post_save, sender=MenuItem)
@receiver(post_delete, sender=MenuItem)
def invalidate_on_item_change(sender, instance, **kwargs):
    MenuService.invalidate_menu_cache(str(instance.restaurant_id))


@receiver(post_save, sender=MenuCategory)
@receiver(post_delete, sender=MenuCategory)
def invalidate_on_category_change(sender, instance, **kwargs):
    MenuService.invalidate_menu_cache(str(instance.restaurant_id))
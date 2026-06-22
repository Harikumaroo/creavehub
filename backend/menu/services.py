"""
CraveHub — Menu Service Layer (Phase 2)
"""

from __future__ import annotations
import logging
from django.core.cache import cache
from django.db.models import Prefetch, Q
from core.exceptions import RestaurantNotFoundError, MenuNotFoundError
from .models import MenuCategory, MenuItem
from .serializers import MenuCategoryWithItemsSerializer, MenuItemSerializer

logger = logging.getLogger(__name__)

MENU_CACHE_KEY_PREFIX = "cravehub:menu:"
MENU_CACHE_TTL = 60 * 10  # 10 minutes


class MenuService:

    @staticmethod
    def get_menu_for_restaurant(restaurant_id: str) -> list[dict]:
        cache_key = f"{MENU_CACHE_KEY_PREFIX}{restaurant_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        available_items_prefetch = Prefetch(
            "items",
            queryset=MenuItem.objects.filter(is_available=True).order_by("name"),
        )

        categories = (
            MenuCategory.objects
            .filter(restaurant_id=restaurant_id)
            .prefetch_related(available_items_prefetch)
            .order_by("display_order", "name")
        )

        if not categories.exists():
            # Fix: correct import path (was using wrong apps prefix)
            from restaurants.models import Restaurant
            if not Restaurant.objects.filter(id=restaurant_id, is_active=True, is_deleted=False).exists():
                raise RestaurantNotFoundError(
                    f"Restaurant '{restaurant_id}' not found or is unavailable."
                )
            return []

        non_empty = [cat for cat in categories if cat.items.all()]
        data = MenuCategoryWithItemsSerializer(non_empty, many=True).data
        result = list(data)
        cache.set(cache_key, result, MENU_CACHE_TTL)
        return result

    @staticmethod
    def get_single_item(item_id: str) -> dict:
        try:
            item = (
                MenuItem.objects
                .select_related("restaurant", "category")
                .get(id=item_id)
            )
        except MenuItem.DoesNotExist:
            raise MenuNotFoundError(f"Menu item '{item_id}' not found.")
        return MenuItemSerializer(item).data

    @staticmethod
    def search_items(query: str, params) -> tuple[list, int]:
        if not query:
            return [], 0
        qs = (
            MenuItem.objects
            .filter(
                Q(name__icontains=query) | Q(description__icontains=query),
                is_available=True,
                restaurant__is_active=True,
                restaurant__is_deleted=False,
            )
            .select_related("restaurant", "category")
            .order_by("name")
        )
        total = qs.count()
        sliced = qs[params.offset: params.offset + params.limit]
        return MenuItemSerializer(sliced, many=True).data, total

    @staticmethod
    def filter_items(filters: dict, params) -> tuple[list, int]:
        qs = (
            MenuItem.objects
            .filter(restaurant__is_active=True, restaurant__is_deleted=False)
            .select_related("restaurant", "category")
        )
        if filters.get("veg") is not None:
            qs = qs.filter(is_veg=filters["veg"])
        if filters.get("category"):
            qs = qs.filter(category_id=filters["category"])
        if filters.get("available") is not None:
            qs = qs.filter(is_available=filters["available"])
        
        if filters.get("max_price") is not None:
            qs = qs.filter(
                Q(discounted_price__lte=filters["max_price"]) | 
                Q(discounted_price__isnull=True, price__lte=filters["max_price"])
            )
            
        if filters.get("is_healthy"):
            # Assume healthy means calories <= 450
            qs = qs.filter(calories__lte=450)

        qs = qs.order_by("name")
        total = qs.count()
        sliced = qs[params.offset: params.offset + params.limit]
        return MenuItemSerializer(sliced, many=True).data, total

    @staticmethod
    def invalidate_menu_cache(restaurant_id: str) -> None:
        cache.delete(f"{MENU_CACHE_KEY_PREFIX}{restaurant_id}")
        logger.info("MenuService: cache invalidated for restaurant %s", restaurant_id)

"""
CraveHub — Categories Service Layer
"""

from __future__ import annotations
import logging
from django.core.cache import cache
from django.db.models import QuerySet
from core.exceptions import CategoryNotFoundError
from .models import Category
from .serializers import CategoryListSerializer

logger = logging.getLogger(__name__)

ACTIVE_CATEGORIES_CACHE_KEY = "cravehub:categories:active"
ACTIVE_CATEGORIES_CACHE_TTL = 60 * 15  # 15 minutes


class CategoryService:

    @staticmethod
    def get_active_categories() -> list[dict]:
        cached = cache.get(ACTIVE_CATEGORIES_CACHE_KEY)
        if cached is not None:
            return cached

        qs = CategoryService._active_qs()
        data = CategoryListSerializer(qs, many=True).data
        result = list(data)
        cache.set(ACTIVE_CATEGORIES_CACHE_KEY, result, ACTIVE_CATEGORIES_CACHE_TTL)
        return result

    @staticmethod
    def get_category_by_id(category_id: str) -> Category:
        try:
            return CategoryService._active_qs().get(id=category_id)
        except Category.DoesNotExist:
            raise CategoryNotFoundError(f"Category '{category_id}' not found.")

    @staticmethod
    def get_category_by_slug(slug: str) -> Category:
        try:
            return CategoryService._active_qs().get(slug=slug)
        except Category.DoesNotExist:
            raise CategoryNotFoundError(f"Category '{slug}' not found.")

    @staticmethod
    def invalidate_cache() -> None:
        cache.delete(ACTIVE_CATEGORIES_CACHE_KEY)
        logger.info("CategoryService: cache invalidated")

    @staticmethod
    def _active_qs() -> QuerySet[Category]:
        return Category.objects.filter(is_active=True).only(
            "id", "name", "slug", "image", "icon", "display_order"
        )
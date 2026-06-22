"""
CraveHub — Banners Service Layer
"""

from __future__ import annotations
import logging
from django.core.cache import cache
from .models import Banner
from .serializers import BannerSerializer

logger = logging.getLogger(__name__)

ACTIVE_BANNERS_CACHE_KEY = "cravehub:banners:active"
ACTIVE_BANNERS_CACHE_TTL = 60 * 5  # 5 minutes


class BannerService:

    @staticmethod
    def get_active_banners() -> list[dict]:
        cached = cache.get(ACTIVE_BANNERS_CACHE_KEY)
        if cached is not None:
            return cached

        qs = (
            Banner.objects.active()
            .only(
                "id", "title", "subtitle", "image",
                "redirect_url", "priority", "start_date", "end_date",
            )
            .order_by("priority", "-created_at")
        )
        data = BannerSerializer(qs, many=True).data
        result = list(data)
        cache.set(ACTIVE_BANNERS_CACHE_KEY, result, ACTIVE_BANNERS_CACHE_TTL)
        return result

    @staticmethod
    def invalidate_cache() -> None:
        cache.delete(ACTIVE_BANNERS_CACHE_KEY)
        logger.info("BannerService: cache invalidated")
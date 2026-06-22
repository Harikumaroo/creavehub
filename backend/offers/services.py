"""
CraveHub — Offers Service Layer
"""

from __future__ import annotations
import logging
from django.core.cache import cache
from core.exceptions import OfferNotFoundError
from .models import Offer
from .serializers import OfferSerializer

logger = logging.getLogger(__name__)

ACTIVE_OFFERS_CACHE_KEY = "cravehub:offers:active"
ACTIVE_OFFERS_CACHE_TTL = 60 * 10  # 10 minutes


class OfferService:

    @staticmethod
    def get_active_offers() -> list[dict]:
        cached = cache.get(ACTIVE_OFFERS_CACHE_KEY)
        if cached is not None:
            return cached

        qs = Offer.objects.active().only(
            "id", "title", "coupon_code", "discount_type",
            "discount_value", "minimum_order_amount",
            "maximum_discount", "expiry_date",
        )
        data = OfferSerializer(qs, many=True).data
        result = list(data)
        cache.set(ACTIVE_OFFERS_CACHE_KEY, result, ACTIVE_OFFERS_CACHE_TTL)
        return result

    @staticmethod
    def get_offer_by_coupon_code(coupon_code: str) -> Offer:
        try:
            return Offer.objects.active().get(coupon_code__iexact=coupon_code)
        except Offer.DoesNotExist:
            raise OfferNotFoundError(
                f"Coupon '{coupon_code}' is invalid or has expired."
            )

    @staticmethod
    def invalidate_cache() -> None:
        cache.delete(ACTIVE_OFFERS_CACHE_KEY)
        logger.info("OfferService: cache invalidated")
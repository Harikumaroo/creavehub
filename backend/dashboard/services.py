"""
CraveHub — Dashboard Service Layer
Aggregates all homepage data in a single optimised query set.
"""

from __future__ import annotations
from django.core.cache import cache
from django.utils import timezone

from banners.models import Banner
from banners.serializers import BannerSerializer
from categories.models import Category
from categories.serializers import CategoryListSerializer
from core.models import AppSector
from core.serializers import AppSectorSerializer
from offers.models import Offer
from offers.serializers import OfferSerializer
from restaurants.models import Restaurant
from restaurants.serializers import RestaurantListSerializer

CACHE_TTL = 60 * 5  # 5 minutes


class DashboardService:

    @staticmethod
    def get_home_data(user=None) -> dict:
        cache_key = "cravehub:dashboard:home"
        cached = cache.get(cache_key)
        if cached:
            # Attach user-specific greeting (not cached)
            cached["user"] = DashboardService._user_info(user)
            return cached

        today = timezone.now().date()

        # Banners
        banners = Banner.objects.active().order_by("priority")[:8]

        # Sectors (dynamic service tiles)
        sectors = AppSector.objects.filter(is_active=True).order_by("display_order")

        # Categories
        categories = Category.objects.filter(
            is_active=True
        ).order_by("display_order")[:12]

        # Offers
        offers = Offer.objects.active().order_by("-created_at")[:12]

        # Featured restaurants
        featured = (
            Restaurant.objects
            .filter(is_active=True, is_deleted=False, is_featured=True)
            .select_related("address")
            .order_by("-rating")[:8]
        )

        # Trending (top rated active open restaurants)
        trending = (
            Restaurant.objects
            .filter(is_active=True, is_deleted=False, is_open=True)
            .select_related("address")
            .order_by("-rating")[:10]
        )

        # All active restaurants (paginated separately but first page here)
        all_restaurants = (
            Restaurant.objects
            .filter(is_active=True, is_deleted=False)
            .select_related("address")
            .order_by("-is_featured", "-rating")[:20]
        )

        data = {
            "sectors":          AppSectorSerializer(sectors, many=True).data,
            "banners":          BannerSerializer(banners, many=True).data,
            "categories":       CategoryListSerializer(categories, many=True).data,
            "offers":           OfferSerializer(offers, many=True).data,
            "featured_restaurants": RestaurantListSerializer(featured, many=True).data,
            "trending_restaurants": RestaurantListSerializer(trending, many=True).data,
            "all_restaurants":  RestaurantListSerializer(all_restaurants, many=True).data,
        }

        cache.set(cache_key, data, CACHE_TTL)
        data["user"] = DashboardService._user_info(user)
        return data

    @staticmethod
    def _user_info(user) -> dict | None:
        if not user or not user.is_authenticated:
            return None
        return {
            "id":           str(user.id),
            "full_name":    user.full_name or "Hey there",
            "mobile_number": user.mobile_number,
            "is_verified":  user.is_verified,
            "avatar":       user.avatar.url if user.avatar else None,
        }

    @staticmethod
    def invalidate_cache():
        cache.delete("cravehub:dashboard:home")

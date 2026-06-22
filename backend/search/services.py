"""
CraveHub — Search Service
Unified PostgreSQL full-text search across restaurants and menu items.
Results cached per query (5 min TTL).
"""

from __future__ import annotations
import logging
from django.core.cache import cache
from django.db.models import Q

from restaurants.models import Restaurant
from restaurants.serializers import RestaurantListSerializer
from menu.models import MenuItem
from menu.serializers import MenuItemSerializer

logger = logging.getLogger(__name__)

SEARCH_CACHE_TTL = 60 * 5


class SearchService:

    @staticmethod
    def unified_search(query: str, user=None, lat: float = None, lng: float = None) -> dict:
        """
        Search restaurants AND menu items in parallel.
        Persists to SearchHistory if user is authenticated.
        Results are cached per normalized query and location.
        """
        import re
        import math
        
        def haversine(lat1, lon1, lat2, lon2):
            if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
                return float('inf')
            R = 6371  # Earth radius in km
            dLat = math.radians(lat2 - lat1)
            dLon = math.radians(lon2 - lon1)
            a = math.sin(dLat/2) * math.sin(dLat/2) + \
                math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
                math.sin(dLon/2) * math.sin(dLon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        q = query.strip()
        if not q:
            return {
                "query": q,
                "restaurants": [],
                "menu_items": [],
                "total_restaurants": 0,
                "total_menu_items": 0,
            }

        cache_key = f"cravehub:search:{q.lower()[:80]}"
        if lat and lng:
            cache_key += f":{round(lat, 2)}:{round(lng, 2)}"
            
        cached = cache.get(cache_key)

        if cached:
            if user and user.is_authenticated:
                SearchService._save_history(user, q)
            return {**cached, "query": q}

        subqueries = [sq.strip() for sq in re.split(r'\s+&\s+|\s+and\s+', q, flags=re.IGNORECASE) if sq.strip()]
        if not subqueries:
            subqueries = [q]

        rest_q_obj = Q()
        item_q_obj = Q()
        for sq in subqueries:
            rest_q_obj |= Q(name__icontains=sq) | Q(description__icontains=sq) | Q(address__city__icontains=sq)
            item_q_obj |= Q(name__icontains=sq) | Q(description__icontains=sq)

        # ── Restaurants ──────────────────────────────────────
        rest_qs = list(
            Restaurant.objects
            .filter(rest_q_obj, is_active=True, is_deleted=False)
            .select_related("address")
            .distinct()
        )

        filtered_rests = []
        for r in rest_qs:
            if lat and lng and hasattr(r, 'address') and r.address:
                dist = haversine(lat, lng, float(r.address.latitude or 0), float(r.address.longitude or 0))
                if dist <= 15:  # 15km radius
                    r.distance = dist
                    filtered_rests.append(r)
            else:
                r.distance = getattr(r, 'distance', float('inf'))
                filtered_rests.append(r)

        # Sort by distance if available, otherwise by rating
        filtered_rests.sort(key=lambda r: (r.distance if hasattr(r, 'distance') and r.distance != float('inf') else 9999, -float(r.rating or 0)))
        filtered_rests = filtered_rests[:20]
        
        # Collect IDs of valid restaurants to filter menu items
        valid_rest_ids = [r.id for r in filtered_rests]

        # ── Menu items ───────────────────────────────────────
        item_qs = list(
            MenuItem.objects
            .filter(
                item_q_obj,
                is_available=True,
                restaurant__is_active=True,
                restaurant__is_deleted=False,
            )
            .select_related("restaurant", "restaurant__address", "category")
        )

        filtered_items = []
        for item in item_qs:
            # Check if restaurant is valid (in our filtered list, or we do a fresh distance check)
            r = item.restaurant
            dist = float('inf')
            if lat and lng and hasattr(r, 'address') and r.address:
                dist = haversine(lat, lng, float(r.address.latitude or 0), float(r.address.longitude or 0))
            if not (lat and lng) or dist <= 15:
                item.distance = dist
                filtered_items.append(item)

        # Sort items by distance, then rating
        filtered_items.sort(key=lambda i: (i.distance if hasattr(i, 'distance') and i.distance != float('inf') else 9999, -float(i.restaurant.rating or 0)))
        filtered_items = filtered_items[:20]

        result = {
            "restaurants":        RestaurantListSerializer(filtered_rests, many=True).data,
            "menu_items":         MenuItemSerializer(filtered_items, many=True).data,
            "total_restaurants":  len(filtered_rests),
            "total_menu_items":   len(filtered_items),
        }

        cache.set(cache_key, result, SEARCH_CACHE_TTL)

        if user and user.is_authenticated:
            SearchService._save_history(user, q)

        return {**result, "query": q}

    @staticmethod
    def get_suggestions(query: str) -> list[str]:
        """Quick autocomplete — returns matching restaurant and menu item names."""
        if not query or len(query) < 1:
            return []
            
        restaurants = (
            Restaurant.objects
            .filter(name__icontains=query, is_active=True, is_deleted=False)
            .values_list("name", flat=True)[:4]
        )
        
        items = (
            MenuItem.objects
            .filter(name__icontains=query, is_available=True)
            .values_list("name", flat=True).distinct()[:6]
        )
        
        # Combine and remove exact duplicates, preserving order roughly
        suggestions = []
        for name in list(restaurants) + list(items):
            if name not in suggestions:
                suggestions.append(name)
                
        return suggestions[:8]

    @staticmethod
    def get_history(user, limit: int = 10) -> list:
        from .models import SearchHistory
        from .serializers import SearchHistorySerializer
        qs = (
            SearchHistory.objects
            .filter(user=user)
            .order_by("-created_at")[:limit]
        )
        return SearchHistorySerializer(qs, many=True).data

    @staticmethod
    def clear_history(user) -> int:
        from .models import SearchHistory
        deleted, _ = SearchHistory.objects.filter(user=user).delete()
        return deleted

    @staticmethod
    def _save_history(user, query: str) -> None:
        from .models import SearchHistory
        try:
            SearchHistory.objects.update_or_create(
                user=user, query=query,
                defaults={"query": query},
            )
        except Exception as exc:
            logger.warning("Search history save failed: %s", exc)

"""
CraveHub — Restaurants Service Layer
"""

from __future__ import annotations
import logging
from typing import Literal
from django.db.models import Prefetch, QuerySet
from core.exceptions import RestaurantNotFoundError
from core.helpers import PaginatedResult, PaginationParams, paginate_queryset
from .models import Restaurant, RestaurantCategory

logger = logging.getLogger(__name__)

SortField = Literal["rating", "delivery_time", "min_order", "name"]

SORT_MAP: dict[str, str] = {
    "rating": "-rating",
    "delivery_time": "average_delivery_time",
    "min_order": "minimum_order_amount",
    "name": "name",
}


class RestaurantService:

    @staticmethod
    def get_restaurant_list(
        params: PaginationParams,
        category_id: str | None = None,
        category_slug: str | None = None,
        is_pure_veg: bool | None = None,
        city: str | None = None,
        sort: str = "rating",
    ) -> PaginatedResult:
        qs = RestaurantService._base_list_qs()
        qs = RestaurantService._apply_filters(
            qs, category_id, category_slug, is_pure_veg, city
        )
        qs = RestaurantService._apply_sort(qs, sort)
        sliced_qs, total_count = paginate_queryset(qs, params)
        return PaginatedResult(
            items=list(sliced_qs),
            total_count=total_count,
            page=params.page,
            page_size=params.page_size,
        )

    @staticmethod
    def get_restaurant_detail(restaurant_id: str) -> Restaurant:
        try:
            return (
                Restaurant.objects
                .filter(is_active=True)
                .select_related("address")
                .prefetch_related(
                    Prefetch(
                        "restaurant_categories",
                        queryset=RestaurantCategory.objects.select_related("category"),
                    )
                )
                .get(id=restaurant_id)
            )
        except Restaurant.DoesNotExist:
            raise RestaurantNotFoundError(
                f"Restaurant '{restaurant_id}' not found or is unavailable."
            )

    @staticmethod
    def _base_list_qs() -> QuerySet[Restaurant]:
        return (
            Restaurant.objects
            .filter(is_active=True)
            .select_related("address")
            .prefetch_related(
                Prefetch(
                    "restaurant_categories",
                    queryset=RestaurantCategory.objects.select_related("category").only(
                        "id", "restaurant_id",
                        "category__id", "category__name", "category__slug",
                    ),
                )
            )
            .only(
                "id", "name", "slug", "logo", "cover_image",
                "rating", "total_reviews", "average_delivery_time",
                "minimum_order_amount", "is_pure_veg", "address__city",
            )
        )

    @staticmethod
    def _apply_filters(qs, category_id, category_slug, is_pure_veg, city):
        if category_id:
            qs = qs.filter(restaurant_categories__category_id=category_id)
        elif category_slug:
            qs = qs.filter(restaurant_categories__category__slug=category_slug)
        if is_pure_veg is not None:
            qs = qs.filter(is_pure_veg=is_pure_veg)
        if city:
            qs = qs.filter(address__city__iexact=city)
        return qs.distinct()

    @staticmethod
    def _apply_sort(qs, sort: str):
        order_field = SORT_MAP.get(sort, "-rating")
        return qs.order_by(order_field)
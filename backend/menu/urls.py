"""
CraveHub — Menu URLs (Phase 2)
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    RestaurantMenuView,
    MenuItemDetailView,
    MenuItemSearchView,
    MenuItemFilterView,
    FavoriteMenuItemViewSet,
)

router = DefaultRouter()
router.register(r"favorites", FavoriteMenuItemViewSet, basename="favorite-menu-item")

app_name = "menu"

urlpatterns = [
    # Full menu for a restaurant
    # GET /api/v1/restaurants/<uuid>/menu/
    path(
        "restaurants/<uuid:restaurant_id>/menu/",
        RestaurantMenuView.as_view(),
        name="restaurant-menu",
    ),
    # Single item detail
    # GET /api/v1/menu/items/<uuid>/
    path(
        "menu/items/<uuid:item_id>/",
        MenuItemDetailView.as_view(),
        name="menu-item-detail",
    ),
    # Search
    # GET /api/v1/menu/search/?q=biryani
    path(
        "menu/search/",
        MenuItemSearchView.as_view(),
        name="menu-search",
    ),
    # Filter
    path(
        "menu/items/",
        MenuItemFilterView.as_view(),
        name="menu-items-filter",
    ),
]

urlpatterns += router.urls

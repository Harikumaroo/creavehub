"""
CraveHub — Menu Views (Phase 2)
"""

from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.exceptions import CraveHubBaseException
from core.helpers import error_response, success_response
from core.helpers.pagination import PaginationParams
from core.helpers.response import paginated_response
from core.permissions import AllowAny

from .services import MenuService


class RestaurantMenuView(APIView):
    """
    GET /api/v1/restaurants/<uuid:restaurant_id>/menu/
    Returns full menu grouped by category.
    Only available items included. Redis cached (10 min TTL).
    """
    permission_classes = [AllowAny]

    def get(self, request: Request, restaurant_id: str):
        try:
            data = MenuService.get_menu_for_restaurant(restaurant_id=str(restaurant_id))
            return success_response(data=data, message="Menu fetched successfully")
        except CraveHubBaseException as exc:
            return error_response(
                exc.message, error_code=exc.error_code, status_code=exc.status_code
            )


class MenuItemDetailView(APIView):
    """
    GET /api/v1/menu/items/<uuid:item_id>/
    Returns a single menu item's full details.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request, item_id: str):
        try:
            data = MenuService.get_single_item(item_id=str(item_id))
            return success_response(data=data, message="Menu item fetched successfully")
        except CraveHubBaseException as exc:
            return error_response(
                exc.message, error_code=exc.error_code, status_code=exc.status_code
            )


class MenuItemSearchView(APIView):
    """
    GET /api/v1/menu/search/?q=biryani
    Full-text search across item names and descriptions.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request):
        query = request.query_params.get("q", "").strip()
        params = PaginationParams.from_request(request)
        data, total = MenuService.search_items(query=query, params=params)
        return paginated_response(
            data=data,
            page=params.page,
            page_size=params.page_size,
            total_count=total,
            message="Search results fetched successfully",
        )


class MenuItemFilterView(APIView):
    """
    GET /api/v1/menu/items/?veg=true&category=<uuid>&available=true
    Filter menu items by various criteria.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request):
        params = PaginationParams.from_request(request)

        filters = {}

        veg = request.query_params.get("veg")
        if veg is not None:
            filters["veg"] = veg.lower() == "true"

        category = request.query_params.get("category")
        if category:
            filters["category"] = category

        available = request.query_params.get("available")
        if available is not None:
            filters["available"] = available.lower() == "true"

        max_price = request.query_params.get("max_price")
        if max_price is not None:
            try:
                filters["max_price"] = float(max_price)
            except ValueError:
                pass
                
        is_healthy = request.query_params.get("is_healthy")
        if is_healthy is not None:
            filters["is_healthy"] = is_healthy.lower() == "true"

        data, total = MenuService.filter_items(filters=filters, params=params)
        return paginated_response(
            data=data,
            page=params.page,
            page_size=params.page_size,
            total_count=total,
            message="Menu items fetched successfully",
        )


from .models import FavoriteMenuItem
from .serializers import FavoriteMenuItemSerializer

class FavoriteMenuItemViewSet(viewsets.ModelViewSet):
    """
    CRUD for User's Favorite Menu Items.
    """
    serializer_class = FavoriteMenuItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteMenuItem.objects.filter(user=self.request.user).select_related("menu_item", "menu_item__restaurant")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

"""
CraveHub — Reviews Views (Phase 3)
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from core.helpers import created_response, error_response, paginated_response, success_response
from core.helpers.pagination import PaginationParams
from core.permissions import IsAuthenticatedAndActive, AllowAny

from .models import RestaurantReview, MenuItemReview
from .serializers import (
    RestaurantReviewSerializer, CreateRestaurantReviewSerializer,
    MenuItemReviewSerializer, CreateMenuItemReviewSerializer,
)


class RestaurantReviewListCreateView(APIView):
    """
    GET  /api/v1/reviews/restaurants/<uuid>/  — list reviews (public)
    POST /api/v1/reviews/restaurants/<uuid>/  — create review (auth required)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticatedAndActive()]

    def get(self, request: Request, restaurant_id):
        params = PaginationParams.from_request(request)
        qs = (
            RestaurantReview.objects
            .filter(restaurant_id=restaurant_id, is_visible=True)
            .select_related("user")
            .order_by("-created_at")
        )
        total  = qs.count()
        sliced = qs[params.offset: params.offset + params.limit]
        serializer = RestaurantReviewSerializer(sliced, many=True)
        return paginated_response(data=serializer.data, page=params.page, page_size=params.page_size, total_count=total, message="Reviews fetched successfully")

    def post(self, request: Request, restaurant_id):
        data = {**request.data, "restaurant": str(restaurant_id)}
        serializer = CreateRestaurantReviewSerializer(data=data, context={"request": request})
        if not serializer.is_valid():
            return error_response("Validation failed", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        review = serializer.save(user=request.user)
        return created_response(data=RestaurantReviewSerializer(review).data, message="Review submitted successfully")


class MenuItemReviewListCreateView(APIView):
    """
    GET  /api/v1/reviews/items/<uuid>/  — list item reviews (public)
    POST /api/v1/reviews/items/<uuid>/  — create item review (auth required)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticatedAndActive()]

    def get(self, request: Request, item_id):
        params = PaginationParams.from_request(request)
        qs = (
            MenuItemReview.objects
            .filter(menu_item_id=item_id, is_visible=True)
            .select_related("user")
            .order_by("-created_at")
        )
        total  = qs.count()
        sliced = qs[params.offset: params.offset + params.limit]
        serializer = MenuItemReviewSerializer(sliced, many=True)
        return paginated_response(data=serializer.data, page=params.page, page_size=params.page_size, total_count=total, message="Reviews fetched successfully")

    def post(self, request: Request, item_id):
        data = {**request.data, "menu_item": str(item_id)}
        serializer = CreateMenuItemReviewSerializer(data=data, context={"request": request})
        if not serializer.is_valid():
            return error_response("Validation failed", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        review = serializer.save(user=request.user)
        return created_response(data=MenuItemReviewSerializer(review).data, message="Review submitted successfully")

"""
CraveHub — Restaurants Views (Phase 2)
"""

from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.mixins import SuccessResponseMixin
from core.helpers import success_response, not_found_response
from core.helpers.pagination import PaginationParams, paginate_queryset
from core.helpers.response import paginated_response

from .models import Restaurant, FavoriteRestaurant
from .serializers import RestaurantDetailSerializer, RestaurantListSerializer, FavoriteRestaurantSerializer


class RestaurantListView(SuccessResponseMixin, generics.ListAPIView):
    """
    GET /api/v1/restaurants/
    Returns paginated list of active restaurants.
    """
    permission_classes = [AllowAny]
    serializer_class = RestaurantListSerializer

    def get_queryset(self):
        return (
            Restaurant.objects
            .filter(is_active=True, is_deleted=False)
            .select_related("address")
            .order_by("-is_featured", "-rating", "name")
        )

    def list(self, request, *args, **kwargs):
        params = PaginationParams.from_request(request)
        queryset = self.get_queryset()
        page_qs, total = paginate_queryset(queryset, params)
        serializer = self.get_serializer(page_qs, many=True)
        return paginated_response(
            data=serializer.data,
            page=params.page,
            page_size=params.page_size,
            total_count=total,
            message="Restaurants fetched successfully",
        )


class RestaurantDetailView(SuccessResponseMixin, generics.RetrieveAPIView):
    """
    GET /api/v1/restaurants/<uuid:pk>/
    Returns full details for a single active restaurant.
    """
    permission_classes = [AllowAny]
    serializer_class = RestaurantDetailSerializer

    def get_queryset(self):
        return (
            Restaurant.objects
            .filter(is_active=True, is_deleted=False)
            .select_related("address")
            .prefetch_related("restaurant_categories__category")
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Restaurant fetched successfully",
        )


class FavoriteRestaurantViewSet(viewsets.ModelViewSet):
    """
    CRUD for User's Favorite Restaurants.
    """
    serializer_class = FavoriteRestaurantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteRestaurant.objects.filter(user=self.request.user).select_related("restaurant")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

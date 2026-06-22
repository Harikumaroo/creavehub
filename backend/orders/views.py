"""
CraveHub — Orders Views (Phase 3)
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from core.exceptions import CraveHubBaseException
from core.helpers import (
    created_response, error_response,
    paginated_response, success_response,
)
from core.helpers.pagination import PaginationParams
from core.permissions import IsAuthenticatedAndActive

from .serializers import (
    CancelOrderSerializer, OrderListSerializer,
    OrderSerializer, PlaceOrderSerializer,
)
from .services import OrderService


class PlaceOrderView(APIView):
    """
    POST /api/v1/orders/place/
    Converts the authenticated user's active cart into an order.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        serializer = PlaceOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            order = OrderService.place_order(
                user=request.user,
                validated_data=serializer.validated_data,
            )
            return created_response(
                data=OrderSerializer(order).data,
                message="Order placed successfully",
            )
        except CraveHubBaseException as exc:
            return error_response(
                exc.message, error_code=exc.error_code,
                status_code=exc.status_code,
            )


class OrderListView(APIView):
    """
    GET /api/v1/orders/
    Returns paginated order history for the authenticated user.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request):
        params = PaginationParams.from_request(request)
        orders, total = OrderService.get_user_orders(
            user=request.user, params=params
        )
        serializer = OrderListSerializer(orders, many=True)
        return paginated_response(
            data=serializer.data,
            page=params.page,
            page_size=params.page_size,
            total_count=total,
            message="Orders fetched successfully",
        )


class OrderDetailView(APIView):
    """
    GET /api/v1/orders/<uuid>/
    Returns full detail of a single order.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request, pk):
        try:
            order = OrderService.get_order(
                user=request.user, order_id=str(pk)
            )
            return success_response(
                data=OrderSerializer(order).data,
                message="Order fetched successfully",
            )
        except CraveHubBaseException as exc:
            return error_response(
                exc.message, error_code=exc.error_code,
                status_code=exc.status_code,
            )


class CancelOrderView(APIView):
    """
    POST /api/v1/orders/<uuid>/cancel/
    Cancels an order if it is still in a cancellable status.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request, pk):
        serializer = CancelOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation failed", errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            order = OrderService.cancel_order(
                user=request.user,
                order_id=str(pk),
                reason=serializer.validated_data.get("reason", ""),
            )
            return success_response(
                data=OrderSerializer(order).data,
                message="Order cancelled successfully",
            )
        except CraveHubBaseException as exc:
            return error_response(
                exc.message, error_code=exc.error_code,
                status_code=exc.status_code,
            )

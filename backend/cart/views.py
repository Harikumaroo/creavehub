"""
CraveHub — Cart Views (Phase 2)
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from core.exceptions import CraveHubBaseException
from core.helpers import error_response, success_response
from core.permissions import IsAuthenticatedAndActive

from .models import Cart
from .serializers import (
    AddCartItemSerializer,
    CartSummarySerializer,
    UpdateCartItemSerializer,
)
from .services import CartService


class CartView(APIView):
    """
    GET /api/v1/cart/
    Returns authenticated user's cart with totals.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request):
        cart = CartService.get_or_create_cart(request.user)
        cart_with_items = (
            Cart.objects
            .prefetch_related("cart_items__menu_item")
            .get(pk=cart.pk)
        )
        serializer = CartSummarySerializer(cart_with_items)
        return success_response(
            data=serializer.data,
            message="Cart fetched successfully",
        )


class AddToCartView(APIView):
    """
    POST /api/v1/cart/add/
    Add item to cart. Increments quantity if already present.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        serializer = AddCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        menu_item = serializer.validated_data["menu_item"]
        quantity = serializer.validated_data["quantity"]

        try:
            cart_item = CartService.add_item(
                user=request.user,
                menu_item=menu_item,
                quantity=quantity,
            )

            return success_response(
                data={"cart_item_id": str(cart_item.pk), "quantity": cart_item.quantity},
                message="Item added to cart",
            )
        except CraveHubBaseException as exc:
            return error_response(
                exc.message, error_code=exc.error_code,
                status_code=exc.status_code,
            )


class UpdateCartItemView(APIView):
    """
    PUT /api/v1/cart/item/<uuid:pk>/
    Update quantity of a specific cart item.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def put(self, request: Request, pk):
        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        cart_item = CartService.update_item_quantity(
            user=request.user,
            cart_item_id=str(pk),
            quantity=serializer.validated_data["quantity"],
        )

        if cart_item is None:
            return error_response(
                message="Cart item not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            data={"cart_item_id": str(cart_item.pk), "quantity": cart_item.quantity},
            message="Cart item updated",
        )


class RemoveCartItemView(APIView):
    """
    DELETE /api/v1/cart/item/<uuid:pk>/
    Remove a single item from the cart.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def delete(self, request: Request, pk):
        removed = CartService.remove_item(
            user=request.user, cart_item_id=str(pk)
        )
        if not removed:
            return error_response(
                message="Cart item not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(message="Item removed from cart")


class ClearCartView(APIView):
    """
    DELETE /api/v1/cart/clear/
    Remove all items from the user's cart.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def delete(self, request: Request):
        CartService.clear_cart(user=request.user)
        return success_response(message="Cart cleared successfully")

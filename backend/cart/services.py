"""
CraveHub — Cart Service Layer (Phase 2)
"""

from __future__ import annotations
from django.db import transaction
from core.exceptions import BadRequestError
from .models import Cart, CartItem


class CartService:

    @staticmethod
    def get_or_create_cart(user) -> Cart:
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    @transaction.atomic
    def add_item(user, menu_item, quantity: int) -> CartItem:
        """
        Add item to cart. Increments quantity if already present.
        Always refreshes price_at_purchase to current effective price.
        """
        if not menu_item.restaurant.is_currently_open:
            raise BadRequestError(f"'{menu_item.restaurant.name}' is currently closed. Cannot add items to cart.")

        cart = CartService.get_or_create_cart(user)
        effective_price = menu_item.effective_price

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={
                "quantity": quantity,
                "price_at_purchase": effective_price,
            },
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.price_at_purchase = effective_price
            cart_item.save(update_fields=["quantity", "price_at_purchase"])

        return cart_item

    @staticmethod
    @transaction.atomic
    def update_item_quantity(user, cart_item_id: str, quantity: int) -> CartItem | None:
        try:
            cart_item = CartItem.objects.select_related("cart__user").get(
                pk=cart_item_id, cart__user=user
            )
        except CartItem.DoesNotExist:
            return None
        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity"])
        return cart_item

    @staticmethod
    @transaction.atomic
    def remove_item(user, cart_item_id: str) -> bool:
        deleted, _ = CartItem.objects.filter(
            pk=cart_item_id, cart__user=user
        ).delete()
        return deleted > 0

    @staticmethod
    @transaction.atomic
    def clear_cart(user) -> None:
        try:
            cart = Cart.objects.get(user=user)
            cart.cart_items.all().delete()
        except Cart.DoesNotExist:
            pass

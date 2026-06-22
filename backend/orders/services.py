"""
CraveHub — Orders Service Layer (Phase 3)
All business logic lives here. Views stay thin.
"""

from __future__ import annotations
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from core.exceptions import (
    BadRequestError, NotFoundError, PermissionDeniedError
)
from cart.models import Cart, CartItem
from offers.models import Offer, DiscountType
from .models import Order, OrderItem, OrderStatusHistory

logger = logging.getLogger(__name__)

DELIVERY_FEE = Decimal("30.00")
TAX_RATE     = Decimal("0.05")


class OrderService:

    @staticmethod
    @transaction.atomic
    def place_order(user, validated_data: dict) -> Order:
        """
        Convert the user's active cart into a confirmed Order.
        Steps:
          1. Validate cart is non-empty
          2. Validate all items still available
          3. Snapshot all prices
          4. Create Order + OrderItems
          5. Log initial status
          6. Clear cart
        """
        # 1. Get cart
        try:
            cart = (
                Cart.objects
                .prefetch_related("cart_items__menu_item__restaurant")
                .get(user=user)
            )
        except Cart.DoesNotExist:
            raise BadRequestError("Your cart is empty.")

        cart_items = list(cart.cart_items.select_related(
            "menu_item__restaurant"
        ).all())

        if not cart_items:
            raise BadRequestError("Your cart is empty.")

        # 2. All items must be from the same restaurant
        restaurant_ids = {item.menu_item.restaurant_id for item in cart_items}
        if len(restaurant_ids) > 1:
            raise BadRequestError(
                "All items must be from the same restaurant."
            )

        restaurant = cart_items[0].menu_item.restaurant

        if not restaurant.is_active or restaurant.is_deleted:
            raise BadRequestError(
                f"'{restaurant.name}' is currently unavailable."
            )

        # 2b. Check if restaurant is open right now
        if not restaurant.is_currently_open:
            raise BadRequestError(
                f"'{restaurant.name}' is currently closed. "
                f"Operating hours: {restaurant.formatted_hours}. "
                f"Please try again during operating hours."
            )

        # 3. Validate availability of every item
        unavailable = [
            item.menu_item.name
            for item in cart_items
            if not item.menu_item.is_available
        ]
        if unavailable:
            raise BadRequestError(
                f"These items are no longer available: {', '.join(unavailable)}"
            )

        # 4. Calculate totals and apply offer
        subtotal   = sum(item.line_total for item in cart_items)
        delivery_fee = DELIVERY_FEE
        discount   = Decimal("0.00")
        
        offer_code = validated_data.get("offer_code")
        if offer_code:
            try:
                offer = Offer.objects.get(coupon_code=offer_code, is_active=True)
                if offer.is_expired:
                    raise BadRequestError("This offer has expired.")
                if subtotal < offer.minimum_order_amount:
                    raise BadRequestError(f"Minimum order amount of ₹{offer.minimum_order_amount} required for this offer.")
                
                if offer.discount_type == DiscountType.PERCENTAGE:
                    calculated = (subtotal * offer.discount_value) / Decimal("100")
                    if offer.maximum_discount and calculated > offer.maximum_discount:
                        discount = offer.maximum_discount
                    else:
                        discount = calculated
                elif offer.discount_type == DiscountType.FLAT:
                    discount = offer.discount_value
                elif offer.discount_type == DiscountType.FREE_DELIVERY:
                    discount = delivery_fee
                    
            except Offer.DoesNotExist:
                raise BadRequestError("Invalid offer code.")

        tax        = round((subtotal - discount) * TAX_RATE, 2)
        if tax < 0: tax = Decimal("0.00")
        
        grand_total = subtotal + delivery_fee + tax - discount
        if grand_total < 0: grand_total = Decimal("0.00")

        # 5. Create Order
        order = Order.objects.create(
            user=user,
            restaurant=restaurant,
            status=Order.Status.PENDING,
            payment_status=Order.PaymentStatus.PENDING,
            payment_method=validated_data["payment_method"],
            subtotal=subtotal,
            discount=discount,
            delivery_fee=delivery_fee,
            tax=tax,
            grand_total=grand_total,
            delivery_address=validated_data["delivery_address"],
            delivery_city=validated_data.get("delivery_city", ""),
            delivery_pincode=validated_data.get("delivery_pincode", ""),
            instructions=validated_data.get("instructions", ""),
            estimated_delivery_time=restaurant.average_delivery_time,
        )

        # 6. Snapshot OrderItems
        order_items = [
            OrderItem(
                order=order,
                menu_item=item.menu_item,
                name=item.menu_item.name,
                price_at_purchase=item.price_at_purchase,
                quantity=item.quantity,
                is_veg=item.menu_item.is_veg,
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # 7. Log status history
        OrderStatusHistory.objects.create(
            order=order,
            status=Order.Status.PENDING,
            note="Order placed successfully.",
            changed_by=user,
        )

        # 8. Clear cart
        cart.cart_items.all().delete()

        logger.info("Order %s placed by user %s", order.id, user.id)
        return order

    @staticmethod
    def get_order(user, order_id: str) -> Order:
        try:
            return (
                Order.objects
                .select_related("restaurant")
                .prefetch_related("items", "status_history")
                .get(pk=order_id, user=user)
            )
        except Order.DoesNotExist:
            raise NotFoundError("Order not found.")

    @staticmethod
    def get_user_orders(user, params) -> tuple[list, int]:
        qs = (
            Order.objects
            .filter(user=user)
            .select_related("restaurant")
            .prefetch_related("items")
            .order_by("-created_at")
        )
        total = qs.count()
        sliced = qs[params.offset: params.offset + params.limit]
        return sliced, total

    @staticmethod
    @transaction.atomic
    def cancel_order(user, order_id: str, reason: str = "") -> Order:
        try:
            order = Order.objects.select_for_update().get(
                pk=order_id, user=user
            )
        except Order.DoesNotExist:
            raise NotFoundError("Order not found.")

        if not order.is_cancellable:
            raise BadRequestError(
                f"Order cannot be cancelled in '{order.status}' status."
            )

        order.status      = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.cancel_reason = reason
        order.save(update_fields=["status", "cancelled_at", "cancel_reason"])

        OrderStatusHistory.objects.create(
            order=order,
            status=Order.Status.CANCELLED,
            note=reason or "Cancelled by user.",
            changed_by=user,
        )

        logger.info("Order %s cancelled by user %s", order.id, user.id)
        return order

    @staticmethod
    @transaction.atomic
    def update_order_status(
        order_id: str, new_status: str,
        changed_by=None, note: str = ""
    ) -> Order:
        """Used by admin/delivery partner to advance order status."""
        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist:
            raise NotFoundError("Order not found.")

        order.status = new_status
        if new_status == Order.Status.DELIVERED:
            order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at"])

        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            note=note,
            changed_by=changed_by,
        )
        return order

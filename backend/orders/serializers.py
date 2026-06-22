"""
CraveHub — Orders Serializers (Phase 3)
"""

from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "menu_item", "name",
            "price_at_purchase", "quantity",
            "is_veg", "line_total",
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ["id", "status", "note", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items          = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    is_cancellable = serializers.ReadOnlyField()
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    restaurant_logo = serializers.CharField(source="restaurant.logo", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "restaurant", "restaurant_name", "restaurant_logo",
            "status", "payment_status", "payment_method",
            "subtotal", "discount", "delivery_fee", "tax", "grand_total",
            "delivery_address", "delivery_city", "delivery_pincode",
            "instructions", "estimated_delivery_time",
            "delivered_at", "cancelled_at", "cancel_reason",
            "is_cancellable", "items", "status_history",
            "created_at", "updated_at",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order history list."""
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    restaurant_logo = serializers.CharField(source="restaurant.logo", read_only=True)
    item_count      = serializers.SerializerMethodField()

    items           = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "restaurant", "restaurant_name", "restaurant_logo",
            "status", "payment_status", "payment_method",
            "grand_total", "item_count", "items",
            "created_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()


# ── Input Serializers ─────────────────────────────────────────────────────── #

class PlaceOrderSerializer(serializers.Serializer):
    payment_method   = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    delivery_address = serializers.CharField(max_length=500)
    delivery_city    = serializers.CharField(max_length=100, required=False, default="")
    delivery_pincode = serializers.CharField(max_length=10,  required=False, default="")
    instructions     = serializers.CharField(max_length=500, required=False, default="")
    offer_code       = serializers.CharField(max_length=30,  required=False, default="", allow_blank=True)


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500, required=False, default="")

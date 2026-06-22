"""
CraveHub — Cart Serializers (Phase 2)
"""

from decimal import Decimal
from rest_framework import serializers
from menu.models import MenuItem
from .models import Cart, CartItem

DELIVERY_FEE = Decimal("30.00")
TAX_RATE = Decimal("0.05")  # 5%


class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    menu_item_image = serializers.CharField(source="menu_item.image", read_only=True)
    is_veg = serializers.BooleanField(source="menu_item.is_veg", read_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "menu_item",
            "menu_item_name",
            "menu_item_image",
            "is_veg",
            "quantity",
            "price_at_purchase",
            "line_total",
        ]


class CartSummarySerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="cart_items", many=True, read_only=True)
    subtotal = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    delivery_fee = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id", "items", "item_count",
            "subtotal", "delivery_fee", "tax", "grand_total",
        ]

    def get_delivery_fee(self, obj):
        return float(DELIVERY_FEE) if obj.subtotal > 0 else 0.0

    def get_tax(self, obj):
        return float(round(obj.subtotal * TAX_RATE, 2))

    def get_grand_total(self, obj):
        if obj.subtotal == 0:
            return 0.0
        return float(obj.subtotal + DELIVERY_FEE + round(obj.subtotal * TAX_RATE, 2))


# ── Input serializers ────────────────────────────────────────────────────── #

class AddCartItemSerializer(serializers.Serializer):
    menu_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        try:
            item = (
                MenuItem.objects
                .select_related("restaurant")
                .get(pk=attrs["menu_item_id"])
            )
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError({"menu_item_id": "Menu item does not exist."})

        if not item.is_available:
            raise serializers.ValidationError(
                {"menu_item_id": "This menu item is currently unavailable."}
            )
        if not item.restaurant.is_active or item.restaurant.is_deleted:
            raise serializers.ValidationError(
                {"menu_item_id": "This restaurant is currently inactive."}
            )

        attrs["menu_item"] = item
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

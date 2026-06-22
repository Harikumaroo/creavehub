"""
CraveHub — Instamart Serializers
"""

from rest_framework import serializers
from .models import InstamartCategory, InstamartStore, InstamartProduct


class InstamartCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = InstamartCategory
        fields = ["id", "name", "image", "display_order"]


class InstamartStoreSerializer(serializers.ModelSerializer):
    is_currently_open = serializers.BooleanField(read_only=True)
    formatted_hours = serializers.CharField(read_only=True)

    class Meta:
        model  = InstamartStore
        fields = [
            "id", "name", "address", "city", "pincode",
            "delivery_time", "delivery_fee", "minimum_order",
            "is_open", "image", "opening_time", "closing_time", "is_24hrs",
            "is_currently_open", "formatted_hours"
        ]


class InstamartProductSerializer(serializers.ModelSerializer):
    effective_price = serializers.ReadOnlyField()
    has_discount    = serializers.ReadOnlyField()
    is_in_stock     = serializers.ReadOnlyField()
    stock_status    = serializers.ReadOnlyField()

    class Meta:
        model  = InstamartProduct
        fields = [
            "id", "name", "description", "brand", "image",
            "price", "discount_price", "effective_price",
            "has_discount", "unit", "stock",
            "is_available", "is_featured",
            "is_in_stock", "stock_status",
            "store", "category",
        ]


class InstamartProductListSerializer(serializers.ModelSerializer):
    """Lightweight for list views."""
    effective_price = serializers.ReadOnlyField()
    has_discount    = serializers.ReadOnlyField()
    is_in_stock     = serializers.ReadOnlyField()
    stock_status    = serializers.ReadOnlyField()

    class Meta:
        model  = InstamartProduct
        fields = [
            "id", "name", "brand", "image",
            "price", "discount_price", "effective_price",
            "has_discount", "unit", "stock", "is_available",
            "is_in_stock", "stock_status", "category",
        ]


from .models import InstamartOrder, InstamartOrderItem

class InstamartOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstamartOrderItem
        fields = ["id", "product", "name", "price_at_purchase", "quantity"]

class InstamartOrderSerializer(serializers.ModelSerializer):
    items = InstamartOrderItemSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = InstamartOrder
        fields = [
            "id", "status", "payment_method", "subtotal", "discount",
            "delivery_fee", "tax", "grand_total", "delivery_address",
            "created_at", "items", "store_name"
        ]

from .models import InstamartCart, InstamartCartItem

class InstamartCartItemSerializer(serializers.ModelSerializer):
    product = InstamartProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = InstamartCartItem
        fields = ["id", "product", "product_id", "quantity"]

class InstamartCartSerializer(serializers.ModelSerializer):
    items = InstamartCartItemSerializer(many=True, read_only=True)

    class Meta:
        model = InstamartCart
        fields = ["id", "items"]

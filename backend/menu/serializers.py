"""
CraveHub — Menu Serializers (Phase 2)
"""

from rest_framework import serializers
from .models import MenuCategory, MenuItem, FavoriteMenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    effective_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id", "name", "description", "image",
            "price", "discounted_price", "effective_price",
            "has_discount", "is_veg", "is_available",
            "is_in_stock", "stock_status",
            "calories", "category", "restaurant", "restaurant_name"
        ]


class MenuCategoryWithItemsSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ["id", "name", "display_order", "items"]

class FavoriteMenuItemSerializer(serializers.ModelSerializer):
    menu_item_detail = MenuItemSerializer(source="menu_item", read_only=True)

    class Meta:
        model = FavoriteMenuItem
        fields = ["id", "menu_item", "menu_item_detail", "created_at"]
        read_only_fields = ["user"]

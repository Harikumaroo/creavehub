"""
CraveHub — Restaurants Serializers (Phase 2)
"""

from rest_framework import serializers
from .models import Restaurant, RestaurantAddress, FavoriteRestaurant


class RestaurantAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantAddress
        fields = [
            "address", "city", "state",
            "country", "pincode",
            "latitude", "longitude",
        ]


from offers.serializers import OfferSerializer

class RestaurantListSerializer(serializers.ModelSerializer):
    address = RestaurantAddressSerializer(read_only=True)
    is_currently_open = serializers.BooleanField(read_only=True)
    is_midnight_restaurant = serializers.BooleanField(read_only=True)
    formatted_hours = serializers.CharField(read_only=True)
    offers = OfferSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            "id", "name", "slug", "description",
            "logo", "cover_image",
            "rating", "total_reviews",
            "average_delivery_time", "minimum_order_amount",
            "delivery_fee", "is_pure_veg",
            "is_open", "is_featured", "is_active",
            "restaurant_type", "address",
            "opening_time", "closing_time", "is_24hrs",
            "is_currently_open", "is_midnight_restaurant",
            "formatted_hours", "offers"
        ]


class RestaurantDetailSerializer(serializers.ModelSerializer):
    address = RestaurantAddressSerializer(read_only=True)
    is_currently_open = serializers.BooleanField(read_only=True)
    is_midnight_restaurant = serializers.BooleanField(read_only=True)
    formatted_hours = serializers.CharField(read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            "id", "name", "slug", "description",
            "logo", "cover_image",
            "rating", "total_reviews",
            "average_delivery_time", "minimum_order_amount",
            "delivery_fee", "preparation_time", "is_pure_veg",
            "is_open", "is_featured", "is_active",
            "restaurant_type", "address",
            "opening_time", "closing_time", "is_24hrs",
            "is_currently_open", "is_midnight_restaurant",
            "formatted_hours",
            "created_at", "updated_at",
        ]


class FavoriteRestaurantSerializer(serializers.ModelSerializer):
    restaurant = RestaurantListSerializer(read_only=True)
    restaurant_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = FavoriteRestaurant
        fields = ["id", "restaurant", "restaurant_id", "created_at"]
        read_only_fields = ["id", "created_at"]

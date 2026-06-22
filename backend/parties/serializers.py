"""
CraveHub — Parties Serializers
"""

from rest_framework import serializers
from .models import PartyPackage, PartyBooking


class PartyPackageSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    stock_status = serializers.CharField(read_only=True)
    restaurant_opening_time = serializers.TimeField(source="restaurant.opening_time", read_only=True)
    restaurant_closing_time = serializers.TimeField(source="restaurant.closing_time", read_only=True)
    restaurant_is_24hrs = serializers.BooleanField(source="restaurant.is_24hrs", read_only=True)
    restaurant_is_currently_open = serializers.BooleanField(source="restaurant.is_currently_open", read_only=True)
    restaurant_formatted_hours = serializers.CharField(source="restaurant.formatted_hours", read_only=True)

    class Meta:
        model = PartyPackage
        fields = [
            "id", "restaurant", "restaurant_name", "name", "description",
            "image", "min_guests", "max_guests", "price_per_person",
            "is_veg", "is_active", "is_in_stock", "stock_status",
            "restaurant_opening_time", "restaurant_closing_time",
            "restaurant_is_24hrs", "restaurant_is_currently_open",
            "restaurant_formatted_hours",
        ]


class PartyBookingSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField(source="package.name", read_only=True)

    class Meta:
        model = PartyBooking
        fields = [
            "id", "package", "package_name", "event_date", "event_time",
            "guest_count", "special_requests", "total_amount", "status",
            "created_at",
        ]
        read_only_fields = ["id", "total_amount", "status", "created_at"]

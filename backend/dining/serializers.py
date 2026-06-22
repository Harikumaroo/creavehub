"""
CraveHub — Dining Serializers
"""

from rest_framework import serializers
from .models import DiningVenue, TableReservation


from restaurants.serializers import RestaurantListSerializer

class DiningVenueSerializer(serializers.ModelSerializer):
    restaurant = RestaurantListSerializer(read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    restaurant_opening_time = serializers.TimeField(source="restaurant.opening_time", read_only=True)
    restaurant_closing_time = serializers.TimeField(source="restaurant.closing_time", read_only=True)
    restaurant_is_24hrs = serializers.BooleanField(source="restaurant.is_24hrs", read_only=True)
    restaurant_is_currently_open = serializers.BooleanField(source="restaurant.is_currently_open", read_only=True)
    restaurant_formatted_hours = serializers.CharField(source="restaurant.formatted_hours", read_only=True)
    distance_km = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = DiningVenue
        fields = [
            "id", "restaurant", "restaurant_name",
            "seating_capacity", "has_ac", "has_outdoor",
            "avg_cost_for_two", "is_active",
            "restaurant_opening_time", "restaurant_closing_time",
            "restaurant_is_24hrs", "restaurant_is_currently_open",
            "restaurant_formatted_hours", "distance_km"
        ]


class TableReservationSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source="venue.restaurant.name", read_only=True)

    class Meta:
        model = TableReservation
        fields = [
            "id", "venue", "venue_name", "date", "time",
            "guest_count", "special_requests", "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

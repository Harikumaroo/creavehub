from rest_framework import serializers
from .models import CateringMenu, CateringInquiry

class CateringMenuSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = CateringMenu
        fields = [
            "id", "restaurant", "restaurant_name", "name", "description",
            "image", "price_per_plate", "min_plates", "cuisine_type",
            "is_veg", "is_active", "is_in_stock", "stock_status", "created_at"
        ]

class CateringInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = CateringInquiry
        fields = [
            "id", "user", "catering_menu", "event_date", "guest_count",
            "venue_address", "budget", "special_requests", "status", "created_at"
        ]
        read_only_fields = ["user", "status"]

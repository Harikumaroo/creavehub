"""
CraveHub — Offers Serializers
"""

from rest_framework import serializers
from .models import Offer, SavedOffer


class OfferSerializer(serializers.ModelSerializer):
    discount_type_display = serializers.CharField(
        source="get_discount_type_display", read_only=True
    )
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id", "title", "coupon_code",
            "discount_type", "discount_type_display",
            "discount_value", "minimum_order_amount",
            "maximum_discount", "expiry_date", "is_expired",
        ]
        read_only_fields = fields


class SavedOfferSerializer(serializers.ModelSerializer):
    offer = OfferSerializer(read_only=True)
    offer_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = SavedOffer
        fields = ["id", "offer", "offer_id", "created_at"]
        read_only_fields = ["id", "created_at"]
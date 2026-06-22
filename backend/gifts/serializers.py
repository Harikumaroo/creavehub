from rest_framework import serializers
from .models import GiftCard, GiftOrder

class GiftCardSerializer(serializers.ModelSerializer):
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = GiftCard
        fields = [
            "id", "name", "description", "image", "amount",
            "is_active", "is_in_stock", "stock_status",
            "created_at", "updated_at",
        ]

class GiftOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftOrder
        fields = [
            "id", "sender", "gift_card", "recipient_name", "recipient_phone",
            "message", "amount", "status", "created_at", "updated_at"
        ]
        read_only_fields = ["sender", "status"]

"""
CraveHub — Payments Serializers (Phase 3)
"""

from rest_framework import serializers
from .models import Payment, SavedPaymentMethod


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "order", "razorpay_order_id", "razorpay_payment_id",
            "amount", "currency", "status", "created_at",
        ]


class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()


class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id   = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature  = serializers.CharField()


class SavedPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPaymentMethod
        fields = [
            "id", "provider", "card_type", "last_four", "is_default", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

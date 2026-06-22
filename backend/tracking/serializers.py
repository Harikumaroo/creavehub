from rest_framework import serializers
from .models import DeliveryAgent, OrderTracking, LocationPing


class DeliveryAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DeliveryAgent
        fields = [
            "id", "full_name", "phone",
            "vehicle_type", "vehicle_number",
            "status", "current_latitude", "current_longitude",
        ]


class OrderTrackingSerializer(serializers.ModelSerializer):
    agent = DeliveryAgentSerializer(read_only=True)

    class Meta:
        model  = OrderTracking
        fields = [
            "id", "order", "agent",
            "agent_latitude", "agent_longitude",
            "dest_latitude", "dest_longitude",
            "eta_minutes", "updated_at",
        ]


class LocationUpdateSerializer(serializers.Serializer):
    order_id  = serializers.UUIDField()
    latitude  = serializers.FloatField()
    longitude = serializers.FloatField()

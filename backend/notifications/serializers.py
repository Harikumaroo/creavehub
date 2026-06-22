"""
CraveHub — Notifications Serializers
"""

from rest_framework import serializers
from .models import Notification, PushToken


class NotificationSerializer(serializers.ModelSerializer):
    notif_type_display = serializers.CharField(
        source="get_notif_type_display", read_only=True
    )

    class Meta:
        model  = Notification
        fields = [
            "id", "title", "body", "notif_type",
            "notif_type_display", "is_read",
            "metadata", "created_at",
        ]


class MarkReadSerializer(serializers.Serializer):
    """Mark specific notifications as read by IDs."""
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(), min_length=1
    )


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PushToken
        fields = ["id", "token", "platform"]

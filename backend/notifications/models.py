"""
CraveHub — Notifications Models
Supports in-app notifications + push notification tracking.
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class Notification(BaseModel):

    class NotificationType(models.TextChoices):
        ORDER_PLACED       = "order_placed",        "Order Placed"
        ORDER_CONFIRMED    = "order_confirmed",     "Order Confirmed"
        ORDER_PREPARING    = "order_preparing",     "Order Preparing"
        ORDER_OUT_DELIVERY = "order_out_delivery",  "Out for Delivery"
        ORDER_DELIVERED    = "order_delivered",     "Order Delivered"
        ORDER_CANCELLED    = "order_cancelled",     "Order Cancelled"
        PAYMENT_SUCCESS    = "payment_success",     "Payment Successful"
        PAYMENT_FAILED     = "payment_failed",      "Payment Failed"
        OFFER_ALERT        = "offer_alert",         "Offer Alert"
        REVIEW_REQUEST     = "review_request",      "Review Request"
        SYSTEM             = "system",              "System"

    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
    )
    title        = models.CharField(max_length=200)
    body         = models.TextField()
    notif_type   = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        db_index=True,
    )
    is_read      = models.BooleanField(default=False, db_index=True)
    # Optional deep-link payload — e.g. {"order_id": "uuid"}
    metadata     = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table  = "notifications"
        ordering  = ["-created_at"]
        indexes   = [
            models.Index(fields=["user", "is_read"],   name="idx_notif_user_read"),
            models.Index(fields=["user", "notif_type"],name="idx_notif_user_type"),
        ]

    def __str__(self):
        return f"{self.notif_type} → {self.user} | {'read' if self.is_read else 'unread'}"


class PushToken(BaseModel):
    """Stores FCM / APNs device tokens per user."""

    class Platform(models.TextChoices):
        ANDROID = "android", "Android"
        IOS     = "ios",     "iOS"
        WEB     = "web",     "Web"

    user     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_tokens",
        db_index=True,
    )
    token    = models.TextField(unique=True)
    platform = models.CharField(
        max_length=10,
        choices=Platform.choices,
        default=Platform.ANDROID,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "push_tokens"
        indexes  = [
            models.Index(fields=["user", "is_active"], name="idx_push_user_active"),
        ]

    def __str__(self):
        return f"{self.platform} token for {self.user}"

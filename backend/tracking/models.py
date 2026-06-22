"""
CraveHub — Tracking Models
Real-time order tracking via Django Channels WebSocket.
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class DeliveryAgent(BaseModel):

    class Status(models.TextChoices):
        AVAILABLE   = "available",   "Available"
        ON_DELIVERY = "on_delivery", "On Delivery"
        OFFLINE     = "offline",     "Offline"

    user         = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="delivery_agent",
        db_index=True,
    )
    full_name    = models.CharField(max_length=200)
    phone        = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=50, default="bike")
    vehicle_number = models.CharField(max_length=20, blank=True, default="")
    status       = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OFFLINE,
        db_index=True,
    )
    # Last known GPS position
    current_latitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_at  = models.DateTimeField(null=True, blank=True)
    is_active    = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "delivery_agents"
        indexes  = [
            models.Index(fields=["status", "is_active"], name="idx_agent_status"),
        ]

    def __str__(self):
        return f"{self.full_name} [{self.status}]"


class OrderTracking(BaseModel):
    """
    Live tracking record for an active order.
    Updated by the delivery agent's app via WebSocket or REST.
    """
    order         = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="tracking",
        db_index=True,
    )
    agent         = models.ForeignKey(
        DeliveryAgent,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="active_deliveries",
    )
    # Agent's current GPS coordinates
    agent_latitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    agent_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # Destination (snapshot from order)
    dest_latitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    dest_longitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # ETA in minutes (recomputed on each location update)
    eta_minutes     = models.PositiveSmallIntegerField(null=True, blank=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "order_tracking"

    def __str__(self):
        return f"Tracking for Order {self.order_id}"


class LocationPing(BaseModel):
    """
    Append-only log of every location update from the delivery agent.
    Used for route replay and SLA analysis.
    """
    tracking  = models.ForeignKey(
        OrderTracking,
        on_delete=models.CASCADE,
        related_name="pings",
        db_index=True,
    )
    latitude  = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        db_table = "location_pings"
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["tracking", "created_at"], name="idx_ping_tracking_ts"),
        ]

    def __str__(self):
        return f"Ping {self.latitude},{self.longitude}"

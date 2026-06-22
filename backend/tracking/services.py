"""
CraveHub — Tracking Service Layer
"""

from __future__ import annotations
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from core.exceptions import NotFoundError, BadRequestError
from .models import DeliveryAgent, OrderTracking, LocationPing

logger = logging.getLogger(__name__)


class TrackingService:

    @staticmethod
    def get_order_tracking(order_id: str, user) -> dict:
        try:
            tracking = (
                OrderTracking.objects
                .select_related("agent", "order")
                .get(order_id=order_id)
            )
        except OrderTracking.DoesNotExist:
            raise NotFoundError("Tracking info not found for this order.")

        if str(tracking.order.user_id) != str(user.id):
            raise NotFoundError("Tracking info not found for this order.")

        from .serializers import OrderTrackingSerializer
        return OrderTrackingSerializer(tracking).data

    @staticmethod
    def update_agent_location(
        agent: DeliveryAgent,
        order_id: str,
        latitude: float,
        longitude: float,
    ) -> OrderTracking:
        try:
            tracking = OrderTracking.objects.get(order_id=order_id, agent=agent)
        except OrderTracking.DoesNotExist:
            raise NotFoundError("No active tracking for this order.")

        tracking.agent_latitude  = latitude
        tracking.agent_longitude = longitude
        tracking.save(update_fields=["agent_latitude", "agent_longitude", "updated_at"])

        # Log ping
        LocationPing.objects.create(
            tracking=tracking,
            latitude=latitude,
            longitude=longitude,
        )

        # Update agent last known position
        agent.current_latitude   = latitude
        agent.current_longitude  = longitude
        agent.last_location_at   = timezone.now()
        agent.save(update_fields=["current_latitude", "current_longitude", "last_location_at"])

        # Push to user's WebSocket channel
        TrackingService._broadcast_location(tracking, latitude, longitude)
        return tracking

    @staticmethod
    def assign_agent(order, agent: DeliveryAgent) -> OrderTracking:
        tracking, _ = OrderTracking.objects.get_or_create(
            order=order,
            defaults={"agent": agent},
        )
        if tracking.agent is None:
            tracking.agent = agent
            tracking.save(update_fields=["agent"])

        agent.status = DeliveryAgent.Status.ON_DELIVERY
        agent.save(update_fields=["status"])
        return tracking

    @staticmethod
    def _broadcast_location(tracking: OrderTracking, lat: float, lng: float) -> None:
        """Push location update to the customer's WebSocket group."""
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        group_name = f"tracking_{tracking.order_id}"
        try:
            async_to_sync(channel_layer.group_send)(group_name, {
                "type":      "location_update",
                "latitude":  float(lat),
                "longitude": float(lng),
                "eta_minutes": tracking.eta_minutes,
                "agent_name":  tracking.agent.full_name if tracking.agent else None,
            })
        except Exception as exc:
            logger.warning("WS broadcast failed: %s", exc)

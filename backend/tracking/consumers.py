"""
CraveHub — Tracking WebSocket Consumer
Customer connects at: ws://<host>/ws/tracking/<order_id>/
Agent sends location updates via REST (TrackingService.update_agent_location)
which broadcasts to this consumer via channel layer.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class OrderTrackingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.order_id  = self.scope["url_route"]["kwargs"]["order_id"]
        self.group_name = f"tracking_{self.order_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("Tracking WS connected: order=%s user=%s", self.order_id, user.id)

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # ── Channel layer event handlers ─────────────────────────

    async def location_update(self, event):
        """Forwards agent location to the connected customer."""
        await self.send(text_data=json.dumps({
            "type":        "location_update",
            "latitude":    event["latitude"],
            "longitude":   event["longitude"],
            "eta_minutes": event.get("eta_minutes"),
            "agent_name":  event.get("agent_name"),
        }))

    async def order_status_change(self, event):
        """Forwards order status changes to the connected customer."""
        await self.send(text_data=json.dumps({
            "type":   "status_change",
            "status": event["status"],
            "note":   event.get("note", ""),
        }))

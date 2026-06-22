"""
CraveHub — WebSocket Consumer for Real-Time Notifications
Uses Django Channels. Connect at: ws://<host>/ws/notifications/
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.user_id    = str(user.id)
        self.group_name = f"notifications_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send unread count on connect
        count = await self._get_unread_count(user)
        await self.send(text_data=json.dumps({
            "type":   "unread_count",
            "count":  count,
        }))
        logger.info("WS connected: user=%s", self.user_id)

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("WS disconnected: user=%s code=%s", getattr(self, "user_id", "?"), code)

    async def receive(self, text_data=None, bytes_data=None):
        """Client can send {"action": "mark_all_read"}"""
        try:
            payload = json.loads(text_data or "{}")
            if payload.get("action") == "mark_all_read":
                user = self.scope["user"]
                await self._mark_all_read(user)
                await self.send(text_data=json.dumps({"type": "all_marked_read"}))
        except Exception as exc:
            logger.warning("WS receive error: %s", exc)

    # ── Channel layer event handlers ─────────────────────────

    async def notification_message(self, event):
        """Handles events pushed via channel layer group_send."""
        await self.send(text_data=json.dumps({
            "type":       "notification",
            "title":      event.get("title"),
            "body":       event.get("body"),
            "notif_type": event.get("notif_type"),
            "metadata":   event.get("metadata", {}),
        }))

    # ── DB helpers ────────────────────────────────────────────

    @database_sync_to_async
    def _get_unread_count(self, user) -> int:
        from .models import Notification
        return Notification.objects.filter(user=user, is_read=False).count()

    @database_sync_to_async
    def _mark_all_read(self, user) -> None:
        from .models import Notification
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)

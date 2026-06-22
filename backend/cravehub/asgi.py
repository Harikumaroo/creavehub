"""
CraveHub — ASGI Configuration
Supports both HTTP (Django) and WebSocket (Channels).

WebSocket routes:
  ws://.../ws/notifications/           — in-app notifications
  ws://.../ws/tracking/<order_id>/     — live order tracking
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")

# Import consumers AFTER setting env var
django_asgi_app = get_asgi_application()

from notifications.consumers import NotificationConsumer
from tracking.consumers import OrderTrackingConsumer
from support.consumers import SupportChatConsumer

websocket_urlpatterns = [
    path("ws/notifications/",                  NotificationConsumer.as_asgi()),
    path("ws/tracking/<uuid:order_id>/",        OrderTrackingConsumer.as_asgi()),
    path("ws/support/tickets/<uuid:ticket_id>/", SupportChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})

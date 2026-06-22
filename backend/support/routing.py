from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/support/tickets/(?P<ticket_id>[\w-]+)/$', consumers.SupportChatConsumer.as_asgi()),
]

from django.urls import path
from .views import (
    NotificationListView, MarkReadView,
    MarkAllReadView, PushTokenView,
)

app_name = "notifications"

urlpatterns = [
    path("",               NotificationListView.as_view(), name="list"),
    path("mark-read/",     MarkReadView.as_view(),         name="mark-read"),
    path("mark-all-read/", MarkAllReadView.as_view(),      name="mark-all-read"),
    path("push-token/",    PushTokenView.as_view(),        name="push-token"),
]

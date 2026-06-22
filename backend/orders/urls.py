"""
CraveHub — Orders URLs (Phase 3)
"""

from django.urls import path
from .views import (
    PlaceOrderView,
    OrderListView,
    OrderDetailView,
    CancelOrderView,
)

app_name = "orders"

urlpatterns = [
    path("place/",           PlaceOrderView.as_view(),  name="order-place"),
    path("",                 OrderListView.as_view(),   name="order-list"),
    path("<uuid:pk>/",       OrderDetailView.as_view(), name="order-detail"),
    path("<uuid:pk>/cancel/",CancelOrderView.as_view(), name="order-cancel"),
]

"""
CraveHub — Cart URLs (Phase 2)
"""

from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
)

app_name = "cart"

urlpatterns = [
    # GET  /api/v1/cart/
    path("", CartView.as_view(), name="cart"),
    # POST /api/v1/cart/add/
    path("add/", AddToCartView.as_view(), name="cart-add"),
    # PUT  /api/v1/cart/item/<uuid>/
    path("item/<uuid:pk>/", UpdateCartItemView.as_view(), name="cart-item-update"),
    # DELETE /api/v1/cart/item/<uuid>/
    path("item/<uuid:pk>/delete/", RemoveCartItemView.as_view(), name="cart-item-delete"),
    # DELETE /api/v1/cart/clear/
    path("clear/", ClearCartView.as_view(), name="cart-clear"),
]

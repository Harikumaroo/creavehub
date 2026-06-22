"""
CraveHub — Cart Models (Phase 2)
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel
from menu.models import MenuItem


class Cart(BaseModel):
    """
    One active cart per user.
    Uses BaseModel for UUID pk + timestamps.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        db_index=True,
    )

    class Meta:
        db_table = "carts"
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart of {self.user}"

    @property
    def subtotal(self):
        return sum(
            item.line_total
            for item in self.cart_items.select_related("menu_item").all()
        )

    @property
    def item_count(self):
        return self.cart_items.count()


class CartItem(BaseModel):
    """
    Individual line item in a cart.
    price_at_purchase is snapshotted when the item is added so price
    changes between add-to-cart and checkout don't silently affect the user.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_items",
        db_index=True,
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="cart_items",
        db_index=True,
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        db_table = "cart_items"
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = [("cart", "menu_item")]
        indexes = [
            models.Index(fields=["cart", "menu_item"], name="idx_cartitem_cart_item"),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    @property
    def line_total(self):
        return self.price_at_purchase * self.quantity

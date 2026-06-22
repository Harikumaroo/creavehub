"""
CraveHub — Gifts Models
Gift cards, food hampers and gifting experiences.
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class GiftCard(BaseModel):
    """A purchasable gift card."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    image = models.URLField(max_length=500, blank=True, default="")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True, db_index=True)
    is_in_stock = models.BooleanField(
        default=True, db_index=True,
        help_text="False = gift card sold out / unavailable.",
    )

    class Meta:
        db_table = "gift_cards"
        ordering = ["amount"]

    def __str__(self):
        return f"{self.name} — ₹{self.amount}"

    @property
    def stock_status(self) -> str:
        if not self.is_active or not self.is_in_stock:
            return "sold_out"
        return "available"


class GiftOrder(BaseModel):
    """A gift purchase made by a user."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gifts_sent",
        db_index=True,
    )
    gift_card = models.ForeignKey(
        GiftCard,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="orders",
    )
    recipient_name = models.CharField(max_length=200)
    recipient_phone = models.CharField(max_length=15)
    message = models.TextField(blank=True, default="")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)

    class Meta:
        db_table = "gift_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Gift from {self.sender} to {self.recipient_name}"

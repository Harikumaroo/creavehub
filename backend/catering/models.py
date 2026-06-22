"""
CraveHub — Catering Models
Event catering inquiries and profiles.
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class CateringMenu(BaseModel):
    """A catering menu offered by a restaurant."""
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="catering_menus",
        db_index=True,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    image = models.URLField(max_length=500, blank=True, default="")
    price_per_plate = models.DecimalField(max_digits=8, decimal_places=2)
    min_plates = models.PositiveIntegerField(default=25)
    cuisine_type = models.CharField(max_length=100, blank=True, default="")
    is_veg = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    is_in_stock = models.BooleanField(
        default=True, db_index=True,
        help_text="False = catering menu currently unavailable / sold out.",
    )

    class Meta:
        db_table = "catering_menus"
        ordering = ["price_per_plate"]

    def __str__(self):
        return f"{self.name} @ {self.restaurant.name}"

    @property
    def stock_status(self) -> str:
        if not self.is_active or not self.is_in_stock:
            return "sold_out"
        return "available"


class CateringInquiry(BaseModel):
    """A catering inquiry submitted by a user."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("contacted", "Contacted"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="catering_inquiries",
        db_index=True,
    )
    catering_menu = models.ForeignKey(
        CateringMenu,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="inquiries",
    )
    event_date = models.DateField(db_index=True)
    guest_count = models.PositiveIntegerField(default=50)
    venue_address = models.TextField(blank=True, default="")
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    special_requests = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)

    class Meta:
        db_table = "catering_inquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Catering inquiry by {self.user} for {self.event_date}"

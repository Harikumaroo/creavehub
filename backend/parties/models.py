"""
CraveHub — Party Orders Models
Bulk orders for events and celebrations.
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class PartyPackage(BaseModel):
    """A pre-defined party package offered by a restaurant."""
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="party_packages",
        db_index=True,
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    image = models.URLField(max_length=500, blank=True, default="")
    min_guests = models.PositiveIntegerField(default=10)
    max_guests = models.PositiveIntegerField(default=100)
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2)
    is_veg = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    is_in_stock = models.BooleanField(
        default=True, db_index=True,
        help_text="False = party team unavailable / sold out.",
    )

    class Meta:
        db_table = "party_packages"
        ordering = ["price_per_person"]

    def __str__(self):
        return f"{self.name} @ {self.restaurant.name}"

    @property
    def stock_status(self) -> str:
        if not self.is_active or not self.is_in_stock:
            return "sold_out"
        return "available"


class PartyBooking(BaseModel):
    """A user's party order / booking."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="party_bookings",
        db_index=True,
    )
    package = models.ForeignKey(
        PartyPackage,
        on_delete=models.CASCADE,
        related_name="bookings",
        db_index=True,
    )
    event_date = models.DateField(db_index=True)
    event_time = models.TimeField()
    guest_count = models.PositiveIntegerField(default=10)
    special_requests = models.TextField(blank=True, default="")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)

    class Meta:
        db_table = "party_bookings"
        ordering = ["-event_date"]

    def __str__(self):
        return f"Party by {self.user} on {self.event_date}"

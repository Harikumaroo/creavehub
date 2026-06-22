"""
CraveHub — Dining Out Models
Table reservations, dine-in offers, and restaurant experiences.
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class DiningVenue(BaseModel):
    """A restaurant venue that supports dine-in bookings."""
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="dining_venues",
        db_index=True,
    )
    seating_capacity = models.PositiveIntegerField(default=50)
    has_ac = models.BooleanField(default=True)
    has_outdoor = models.BooleanField(default=False)
    avg_cost_for_two = models.DecimalField(max_digits=8, decimal_places=2, default=500)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "dining_venues"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dining @ {self.restaurant.name}"


class TableReservation(BaseModel):
    """A dine-in table reservation by a user."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dining_reservations",
        db_index=True,
    )
    venue = models.ForeignKey(
        DiningVenue,
        on_delete=models.CASCADE,
        related_name="reservations",
        db_index=True,
    )
    date = models.DateField(db_index=True)
    time = models.TimeField()
    guest_count = models.PositiveSmallIntegerField(default=2)
    special_requests = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)

    class Meta:
        db_table = "dining_reservations"
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"Reservation for {self.user} at {self.venue} on {self.date}"

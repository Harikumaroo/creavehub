"""
CraveHub — Dining Admin
"""

from django.contrib import admin
from .models import DiningVenue, TableReservation


@admin.register(DiningVenue)
class DiningVenueAdmin(admin.ModelAdmin):
    list_display = ["restaurant", "seating_capacity", "avg_cost_for_two", "has_ac", "has_outdoor", "is_active"]
    list_filter = ["is_active", "has_ac", "has_outdoor"]
    search_fields = ["restaurant__name"]


@admin.register(TableReservation)
class TableReservationAdmin(admin.ModelAdmin):
    list_display = ["user", "venue", "date", "time", "guest_count", "status"]
    list_filter = ["status", "date"]
    search_fields = ["user__full_name", "venue__restaurant__name"]

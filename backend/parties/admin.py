"""
CraveHub — Parties Admin
"""

from django.contrib import admin
from .models import PartyPackage, PartyBooking


@admin.register(PartyPackage)
class PartyPackageAdmin(admin.ModelAdmin):
    list_display = ["name", "restaurant", "min_guests", "max_guests", "price_per_person", "is_veg", "is_active"]
    list_filter = ["is_active", "is_veg"]
    search_fields = ["name", "restaurant__name"]


@admin.register(PartyBooking)
class PartyBookingAdmin(admin.ModelAdmin):
    list_display = ["user", "package", "event_date", "guest_count", "total_amount", "status"]
    list_filter = ["status", "event_date"]
    search_fields = ["user__full_name"]

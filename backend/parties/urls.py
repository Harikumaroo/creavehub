"""
CraveHub — Parties URLs
"""

from django.urls import path
from .views import PartyPackageListView, PartyBookingCreateView, MyPartyBookingsView

app_name = "parties"

urlpatterns = [
    path("packages/", PartyPackageListView.as_view(), name="package-list"),
    path("bookings/", PartyBookingCreateView.as_view(), name="booking-create"),
    path("my-bookings/", MyPartyBookingsView.as_view(), name="my-bookings"),
]

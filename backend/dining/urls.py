"""
CraveHub — Dining URLs
"""

from django.urls import path
from .views import DiningVenueListView, DiningVenueDetailView, ReservationCreateView, MyReservationsView

app_name = "dining"

urlpatterns = [
    path("venues/", DiningVenueListView.as_view(), name="venue-list"),
    path("venues/<uuid:pk>/", DiningVenueDetailView.as_view(), name="venue-detail"),
    path("reservations/", ReservationCreateView.as_view(), name="reservation-create"),
    path("my-reservations/", MyReservationsView.as_view(), name="my-reservations"),
]

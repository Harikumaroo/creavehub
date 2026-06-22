"""
CraveHub — Dining Views
"""

from datetime import time as dt_time

from rest_framework.views import APIView
from rest_framework.request import Request

from core.helpers import success_response, error_response
from core.permissions import AllowAny

from .models import DiningVenue, TableReservation
from .serializers import DiningVenueSerializer, TableReservationSerializer


import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

class DiningVenueListView(APIView):
    """GET /api/v1/dining/venues/ — list active venues."""
    permission_classes = [AllowAny]

    def get(self, request: Request):
        venues = DiningVenue.objects.filter(is_active=True).select_related("restaurant", "restaurant__address").prefetch_related("restaurant__offers")
        
        has_offers = request.query_params.get("has_offers")
        if has_offers and has_offers.lower() == "true":
            venues = venues.filter(restaurant__offers__isnull=False).distinct()
            
        venues = list(venues.order_by("avg_cost_for_two"))

        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = request.query_params.get("radius", 10)
        
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                radius = float(radius)
                filtered_venues = []
                for v in venues:
                    if hasattr(v.restaurant, 'address') and v.restaurant.address:
                        addr = v.restaurant.address
                        if addr.latitude and addr.longitude:
                            dist = haversine(lat, lng, float(addr.latitude), float(addr.longitude))
                            v.distance_km = round(dist, 1)
                            if dist <= radius:
                                filtered_venues.append(v)
                    else:
                        filtered_venues.append(v)
                venues = filtered_venues
            except ValueError:
                pass
                
        data = DiningVenueSerializer(venues, many=True).data
        return success_response(data=data, message="Dining venues fetched")


class DiningVenueDetailView(APIView):
    """GET /api/v1/dining/venues/<uuid>/ — single venue detail."""
    permission_classes = [AllowAny]

    def get(self, request: Request, pk):
        try:
            venue = DiningVenue.objects.select_related("restaurant").get(pk=pk, is_active=True)
        except DiningVenue.DoesNotExist:
            return error_response("Venue not found", status_code=404)
        return success_response(data=DiningVenueSerializer(venue).data, message="Venue fetched")


class ReservationCreateView(APIView):
    """POST /api/v1/dining/reservations/ — create a reservation."""

    def post(self, request: Request):
        serializer = TableReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ── Time-based validation ───────────────────────────────
        venue_id = serializer.validated_data.get("venue")
        requested_time = serializer.validated_data.get("time")

        # venue may be a DiningVenue instance or a PK depending on serializer config
        if hasattr(venue_id, "restaurant"):
            venue = venue_id
        else:
            try:
                venue = DiningVenue.objects.select_related("restaurant").get(pk=venue_id, is_active=True)
            except DiningVenue.DoesNotExist:
                return error_response("Venue not found", status_code=404)

        restaurant = venue.restaurant

        if requested_time and not restaurant.is_open_at(requested_time):
            return error_response(
                f"'{restaurant.name}' is closed at the requested time. "
                f"Operating hours: {restaurant.formatted_hours}.",
                status_code=400,
            )

        if not restaurant.is_currently_open and not restaurant.is_24hrs:
            # Even if the requested time is valid, warn if restaurant is
            # currently toggled off via is_open flag.
            if not restaurant.is_open:
                return error_response(
                    f"'{restaurant.name}' is currently closed. "
                    f"Operating hours: {restaurant.formatted_hours}.",
                    status_code=400,
                )

        serializer.save(user=request.user)
        return success_response(data=serializer.data, message="Reservation created", status_code=201)


class MyReservationsView(APIView):
    """GET /api/v1/dining/my-reservations/ — list user's reservations."""

    def get(self, request: Request):
        reservations = (
            TableReservation.objects
            .filter(user=request.user)
            .select_related("venue__restaurant")
            .order_by("-date")
        )
        data = TableReservationSerializer(reservations, many=True).data
        return success_response(data=data, message="Reservations fetched")

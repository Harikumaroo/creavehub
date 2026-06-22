"""
CraveHub — Parties Views
"""

from rest_framework.views import APIView
from rest_framework.request import Request

from core.helpers import success_response, error_response
from core.permissions import AllowAny

from .models import PartyPackage, PartyBooking
from .serializers import PartyPackageSerializer, PartyBookingSerializer


class PartyPackageListView(APIView):
    """GET /api/v1/parties/packages/ — list active packages."""
    permission_classes = [AllowAny]

    def get(self, request: Request):
        packages = (
            PartyPackage.objects
            .filter(is_active=True)
            .select_related("restaurant")
            .order_by("price_per_person")
        )
        data = PartyPackageSerializer(packages, many=True).data
        return success_response(data=data, message="Party packages fetched")


class PartyBookingCreateView(APIView):
    """POST /api/v1/parties/bookings/ — create a party booking."""

    def post(self, request: Request):
        serializer = PartyBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ── Time-based validation ───────────────────────────────
        package = serializer.validated_data.get("package")
        event_time = serializer.validated_data.get("event_time")

        # Resolve package → restaurant
        if hasattr(package, "restaurant"):
            pkg = package
        else:
            try:
                pkg = PartyPackage.objects.select_related("restaurant").get(pk=package, is_active=True)
            except PartyPackage.DoesNotExist:
                return error_response("Party package not found", status_code=404)

        restaurant = pkg.restaurant

        # Check if package is in stock
        if not pkg.is_in_stock:
            return error_response(
                f"'{pkg.name}' is currently sold out / unavailable.",
                status_code=400,
            )

        # Check if restaurant is open at the requested event time
        if event_time and not restaurant.is_open_at(event_time):
            return error_response(
                f"'{restaurant.name}' is closed at the requested time. "
                f"Operating hours: {restaurant.formatted_hours}. "
                f"Please choose a time within operating hours.",
                status_code=400,
            )

        if not restaurant.is_open:
            return error_response(
                f"'{restaurant.name}' is currently closed. "
                f"Operating hours: {restaurant.formatted_hours}.",
                status_code=400,
            )

        booking = serializer.save(user=request.user)
        # Calculate total
        booking.total_amount = booking.package.price_per_person * booking.guest_count
        booking.save(update_fields=["total_amount"])
        return success_response(data=PartyBookingSerializer(booking).data, message="Party booking created", status_code=201)


class MyPartyBookingsView(APIView):
    """GET /api/v1/parties/my-bookings/ — user's party bookings."""

    def get(self, request: Request):
        bookings = (
            PartyBooking.objects
            .filter(user=request.user)
            .select_related("package__restaurant")
            .order_by("-event_date")
        )
        data = PartyBookingSerializer(bookings, many=True).data
        return success_response(data=data, message="Party bookings fetched")

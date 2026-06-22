"""
CraveHub — Tracking Views
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from core.exceptions import CraveHubBaseException
from core.helpers import error_response, success_response
from core.permissions import IsAuthenticatedAndActive

from .serializers import LocationUpdateSerializer
from .services import TrackingService


class OrderTrackingView(APIView):
    """
    GET /api/v1/tracking/orders/<uuid>/
    Returns current tracking info (agent location + ETA) for an order.
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request, order_id):
        try:
            data = TrackingService.get_order_tracking(
                order_id=str(order_id), user=request.user
            )
            return success_response(data=data, message="Tracking info fetched successfully")
        except CraveHubBaseException as exc:
            return error_response(exc.message, status_code=exc.status_code)


class AgentLocationUpdateView(APIView):
    """
    POST /api/v1/tracking/location/
    Called by the delivery agent's app to push GPS coordinates.
    Body: {"order_id": "uuid", "latitude": 13.0827, "longitude": 80.2707}
    """
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request):
        serializer = LocationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Validation failed", errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            agent = request.user.delivery_agent
        except Exception:
            return error_response(
                "You are not registered as a delivery agent.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        try:
            tracking = TrackingService.update_agent_location(
                agent=agent,
                order_id=str(serializer.validated_data["order_id"]),
                latitude=serializer.validated_data["latitude"],
                longitude=serializer.validated_data["longitude"],
            )
            return success_response(
                data={"eta_minutes": tracking.eta_minutes},
                message="Location updated successfully",
            )
        except CraveHubBaseException as exc:
            return error_response(exc.message, status_code=exc.status_code)

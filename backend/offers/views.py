"""
CraveHub — Offers Views
"""

from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import viewsets
from core.exceptions import CraveHubBaseException
from core.helpers import error_response, success_response
from core.permissions import AllowAny, IsAuthenticated
from .services import OfferService
from .models import SavedOffer
from .serializers import SavedOfferSerializer


class OfferListView(APIView):
    """
    GET /api/v1/offers/
    Returns all active, non-expired promotional offers.
    """
    permission_classes = [AllowAny]
    throttle_scope = "public"

    def get(self, request: Request):
        try:
            data = OfferService.get_active_offers()
            return success_response(data=data, message="Offers fetched successfully")
        except CraveHubBaseException as exc:
            return error_response(
                exc.message, error_code=exc.error_code, status_code=exc.status_code
            )


class SavedOfferViewSet(viewsets.ModelViewSet):
    """
    CRUD for User's Saved Offers.
    """
    serializer_class = SavedOfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedOffer.objects.filter(user=self.request.user).select_related("offer")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
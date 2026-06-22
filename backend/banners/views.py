"""
CraveHub — Banners Views
"""

from rest_framework.request import Request
from rest_framework.views import APIView
from core.exceptions import CraveHubBaseException
from core.helpers import error_response, success_response
from core.permissions import AllowAny
from .services import BannerService


class BannerListView(APIView):
    """
    GET /api/v1/banners/
    Returns active banners sorted by priority.
    Active = is_active=True AND today within start_date to end_date.
    """
    permission_classes = [AllowAny]
    throttle_scope = "public"

    def get(self, request: Request):
        try:
            data = BannerService.get_active_banners()
            return success_response(data=data, message="Banners fetched successfully")
        except CraveHubBaseException as exc:
            return error_response(
                exc.message, error_code=exc.error_code, status_code=exc.status_code
            )
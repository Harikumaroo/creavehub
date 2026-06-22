"""
CraveHub — Dashboard Views
"""

from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.helpers import success_response, error_response
from core.permissions import AllowAny

from .services import DashboardService


class DashboardHomeView(APIView):
    """
    GET /api/v1/dashboard/
    Single endpoint that returns everything the home screen needs:
      - user info (if authenticated)
      - banners
      - categories
      - offers
      - featured restaurants
      - trending restaurants
      - all restaurants (first page)
    Auth is optional — unauthenticated users get the same data minus user info.
    """
    permission_classes = [AllowAny]
    # Try to authenticate but don't reject unauthenticated users
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request):
        try:
            data = DashboardService.get_home_data(user=request.user)
            return success_response(data=data, message="Dashboard loaded successfully")
        except Exception as exc:
            return error_response(str(exc))

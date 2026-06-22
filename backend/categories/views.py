from rest_framework.request import Request
from rest_framework.views import APIView
from core.exceptions import CraveHubBaseException
from core.helpers import error_response, success_response
from core.permissions import AllowAny
from .services import CategoryService


class CategoryListView(APIView):
    """
    GET /api/v1/categories/
    Returns all active food categories ordered by display_order.
    Served from Redis cache (15-minute TTL).
    """

    permission_classes = [AllowAny]
    throttle_scope = "public"

    def get(self, request: Request):
        try:
            data = CategoryService.get_active_categories()
            return success_response(
                data=data,
                message="Categories fetched successfully",
            )
        except CraveHubBaseException as exc:
            return error_response(
                message=exc.message,
                error_code=exc.error_code,
                status_code=exc.status_code,
            )
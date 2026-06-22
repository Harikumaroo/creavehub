"""
CraveHub — Search Views
"""

from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.helpers import success_response, error_response
from core.permissions import AllowAny, IsAuthenticatedAndActive

from .services import SearchService


class UnifiedSearchView(APIView):
    """
    GET /api/v1/search/?q=biryani
    Searches restaurants AND menu items. Auth optional (saves history if logged in).
    """
    permission_classes     = [AllowAny]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request):
        query = request.query_params.get("q", "").strip()
        lat_str = request.query_params.get("lat")
        lng_str = request.query_params.get("lng")
        
        lat = float(lat_str) if lat_str else None
        lng = float(lng_str) if lng_str else None

        if not query:
            return error_response("Search query 'q' is required.")
        result = SearchService.unified_search(query=query, user=request.user, lat=lat, lng=lng)
        return success_response(data=result, message="Search results fetched successfully")


class SearchSuggestionsView(APIView):
    """
    GET /api/v1/search/suggestions/?q=bir
    Returns quick autocomplete suggestions (restaurant names).
    """
    permission_classes = [AllowAny]

    def get(self, request: Request):
        query       = request.query_params.get("q", "").strip()
        suggestions = SearchService.get_suggestions(query)
        return success_response(
            data={"suggestions": suggestions},
            message="Suggestions fetched",
        )


class SearchHistoryView(APIView):
    """
    GET    /api/v1/search/history/  — fetch user's recent searches
    DELETE /api/v1/search/history/  — clear all search history
    """
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request):
        history = SearchService.get_history(user=request.user)
        return success_response(data={"history": history}, message="Search history fetched")

    def delete(self, request: Request):
        deleted = SearchService.clear_history(user=request.user)
        return success_response(
            data={"deleted": deleted},
            message="Search history cleared",
        )

from django.urls import path
from .views import UnifiedSearchView, SearchSuggestionsView, SearchHistoryView

app_name = "search"

urlpatterns = [
    path("",            UnifiedSearchView.as_view(),    name="unified-search"),
    path("suggestions/",SearchSuggestionsView.as_view(),name="suggestions"),
    path("history/",    SearchHistoryView.as_view(),    name="history"),
]

from django.urls import path
from .views import OfferListView, SavedOfferViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'saved', SavedOfferViewSet, basename='saved-offer')

app_name = "offers"

urlpatterns = [
    path("", OfferListView.as_view(), name="offer-list"),
]

urlpatterns += router.urls
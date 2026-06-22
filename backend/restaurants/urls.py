from django.urls import path
from .views import RestaurantDetailView, RestaurantListView, FavoriteRestaurantViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'favorites', FavoriteRestaurantViewSet, basename='favorite')

app_name = "restaurants"

urlpatterns = [
    path("", RestaurantListView.as_view(), name="restaurant-list"),
    path("<uuid:pk>/", RestaurantDetailView.as_view(), name="restaurant-detail"),
]

urlpatterns += router.urls
from django.urls import path
from .views import RestaurantReviewListCreateView, MenuItemReviewListCreateView

app_name = "reviews"

urlpatterns = [
    path("restaurants/<uuid:restaurant_id>/", RestaurantReviewListCreateView.as_view(), name="restaurant-reviews"),
    path("items/<uuid:item_id>/",             MenuItemReviewListCreateView.as_view(),   name="item-reviews"),
]

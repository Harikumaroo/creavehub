from django.urls import path
from .views import OrderTrackingView, AgentLocationUpdateView

app_name = "tracking"

urlpatterns = [
    path("orders/<uuid:order_id>/", OrderTrackingView.as_view(),      name="order-tracking"),
    path("location/",               AgentLocationUpdateView.as_view(), name="location-update"),
]

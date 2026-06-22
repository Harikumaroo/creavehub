from django.urls import path
from .views import InitiatePaymentView, VerifyPaymentView, PaymentHistoryView, DevSimulatePaymentView, SavedPaymentMethodViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'saved-methods', SavedPaymentMethodViewSet, basename='saved-method')

app_name = "payments"

urlpatterns = [
    path("initiate/", InitiatePaymentView.as_view(), name="payment-initiate"),
    path("verify/",   VerifyPaymentView.as_view(),   name="payment-verify"),
    path("history/",  PaymentHistoryView.as_view(),  name="payment-history"),
    path("dev/simulate/", DevSimulatePaymentView.as_view(), name="payment-dev-simulate"),
]

urlpatterns += router.urls

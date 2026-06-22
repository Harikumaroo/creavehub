from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FAQCategoryViewSet, FAQViewSet, 
    SupportTicketViewSet, RefundViewSet
)

router = DefaultRouter()
router.register(r'faq-categories', FAQCategoryViewSet, basename='faq-category')
router.register(r'faqs', FAQViewSet, basename='faq')
router.register(r'tickets', SupportTicketViewSet, basename='ticket')
router.register(r'refunds', RefundViewSet, basename='refund')

urlpatterns = [
    path('', include(router.urls)),
]

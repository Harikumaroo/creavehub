from django.urls import path
from . import views

app_name = "gifts"

urlpatterns = [
    path("cards/", views.GiftCardListView.as_view(), name="gift_cards_list"),
    path("orders/", views.GiftOrderCreateView.as_view(), name="gift_order_create"),
]

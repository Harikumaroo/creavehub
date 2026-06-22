from django.urls import path
from . import views

app_name = "catering"

urlpatterns = [
    path("menus/", views.CateringMenuListView.as_view(), name="catering_menus_list"),
    path("inquiries/", views.CateringInquiryCreateView.as_view(), name="catering_inquiry_create"),
]

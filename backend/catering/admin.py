from django.contrib import admin
from .models import CateringMenu, CateringInquiry

@admin.register(CateringMenu)
class CateringMenuAdmin(admin.ModelAdmin):
    list_display = ["name", "restaurant", "price_per_plate", "min_plates", "is_veg", "is_active"]
    list_filter = ["is_active", "is_veg"]
    search_fields = ["name", "restaurant__name"]

@admin.register(CateringInquiry)
class CateringInquiryAdmin(admin.ModelAdmin):
    list_display = ["user", "catering_menu", "event_date", "guest_count", "status"]
    list_filter = ["status"]
    search_fields = ["user__email", "user__first_name"]

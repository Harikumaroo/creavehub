"""
CraveHub — Offers Admin
"""

from django.contrib import admin
from .models import Offer, SavedOffer
from .services import OfferService


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = [
        "coupon_code", "title", "discount_type", "discount_value",
        "minimum_order_amount", "maximum_discount",
        "expiry_date", "is_active", "is_expired_display",
    ]
    list_filter = ["is_active", "discount_type", "expiry_date"]
    search_fields = ["coupon_code", "title"]
    list_editable = ["is_active"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]

    @admin.display(description="Expired?", boolean=True)
    def is_expired_display(self, obj):
        return obj.is_expired

    @admin.action(description="Activate selected offers")
    def activate(self, request, queryset):
        queryset.update(is_active=True)
        OfferService.invalidate_cache()
        self.message_user(request, f"{queryset.count()} offers activated.")

    @admin.action(description="Deactivate selected offers")
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
        OfferService.invalidate_cache()
        self.message_user(request, f"{queryset.count()} offers deactivated.")

    actions = [activate, deactivate]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        OfferService.invalidate_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        OfferService.invalidate_cache()


@admin.register(SavedOffer)
class SavedOfferAdmin(admin.ModelAdmin):
    list_display = ["user", "offer", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__mobile_number", "offer__coupon_code"]
    readonly_fields = ["id", "created_at"]
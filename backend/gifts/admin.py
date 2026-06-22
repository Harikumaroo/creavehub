"""
CraveHub — Gifts Admin
"""

from django.contrib import admin
from .models import GiftCard, GiftOrder


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(GiftOrder)
class GiftOrderAdmin(admin.ModelAdmin):
    list_display = ["sender", "gift_card", "recipient_name", "amount", "status"]
    list_filter = ["status"]
    search_fields = ["sender__full_name", "recipient_name"]

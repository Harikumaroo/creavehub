"""
CraveHub — Banners Admin
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Banner
from .services import BannerService


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = [
        "title", "priority", "is_active",
        "start_date", "end_date", "is_currently_active_display", "image_preview",
    ]
    list_filter = ["is_active", "start_date", "end_date"]
    search_fields = ["title", "subtitle"]
    list_editable = ["priority", "is_active"]
    ordering = ["priority"]
    readonly_fields = ["id", "created_at", "updated_at", "image_preview"]

    @admin.display(description="Live?", boolean=True)
    def is_currently_active_display(self, obj):
        return obj.is_currently_active

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:6px;" />', obj.image
            )
        return "—"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        BannerService.invalidate_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        BannerService.invalidate_cache()
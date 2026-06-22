"""
CraveHub — Categories Admin
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category
from .services import CategoryService


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name", "slug", "display_order",
        "is_active", "image_preview", "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["display_order", "name"]
    readonly_fields = ["id", "created_at", "updated_at", "image_preview"]
    list_editable = ["display_order", "is_active"]
    list_per_page = 50

    fieldsets = (
        ("Identity", {"fields": ("id", "name", "slug")}),
        ("Media", {"fields": ("image_preview", "image", "icon")}),
        ("Settings", {"fields": ("display_order", "is_active")}),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;" />', obj.image
            )
        return "—"

    @admin.action(description="Activate selected categories")
    def activate(self, request, queryset):
        queryset.update(is_active=True)
        CategoryService.invalidate_cache()
        self.message_user(request, f"{queryset.count()} categories activated.")

    @admin.action(description="Deactivate selected categories")
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
        CategoryService.invalidate_cache()
        self.message_user(request, f"{queryset.count()} categories deactivated.")

    actions = [activate, deactivate]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        CategoryService.invalidate_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        CategoryService.invalidate_cache()
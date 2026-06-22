"""
CraveHub — Restaurants Admin (Phase 2)
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, RestaurantAddress, RestaurantCategory, FavoriteRestaurant


class RestaurantAddressInline(admin.StackedInline):
    model = RestaurantAddress
    extra = 0
    fields = ["address", "city", "state", "country", "pincode", "latitude", "longitude"]


class RestaurantCategoryInline(admin.TabularInline):
    model = RestaurantCategory
    extra = 1
    autocomplete_fields = ["category"]


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = [
        "name", "slug", "restaurant_type", "rating", "average_delivery_time",
        "delivery_fee", "is_open", "is_featured", "is_pure_veg",
        "is_active", "is_deleted", "logo_preview", "created_at",
    ]
    list_filter = [
        "is_active", "is_deleted", "is_pure_veg",
        "is_open", "is_featured", "restaurant_type", "created_at",
    ]
    search_fields = ["name", "slug"]
    ordering = ["-rating"]
    readonly_fields = ["id", "slug", "created_at", "updated_at", "logo_preview"]
    list_editable = ["is_active", "is_open", "is_featured"]
    list_per_page = 50
    inlines = [RestaurantAddressInline, RestaurantCategoryInline]

    fieldsets = (
        ("Identity", {"fields": ("id", "name", "slug", "description", "restaurant_type")}),
        ("Media", {"fields": ("logo_preview", "logo", "cover_image")}),
        ("Stats", {
            "fields": (
                "rating", "total_reviews", "average_delivery_time",
                "minimum_order_amount", "delivery_fee", "preparation_time",
            )
        }),
        ("Settings", {
            "fields": ("is_pure_veg", "is_open", "is_featured", "is_active", "is_deleted")
        }),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Logo")
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;" />', obj.logo
            )
        return "—"

    @admin.action(description="Soft delete selected restaurants")
    def soft_delete(self, request, queryset):
        for obj in queryset:
            obj.soft_delete()
        self.message_user(request, f"{queryset.count()} restaurants soft-deleted.")

    actions = [soft_delete]

    def get_queryset(self, request):
        return Restaurant.all_objects.all()


@admin.register(RestaurantAddress)
class RestaurantAddressAdmin(admin.ModelAdmin):
    list_display = ["restaurant", "city", "state", "pincode"]
    search_fields = ["restaurant__name", "city", "pincode"]
    list_filter = ["city", "state"]


@admin.register(FavoriteRestaurant)
class FavoriteRestaurantAdmin(admin.ModelAdmin):
    list_display = ["user", "restaurant", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__mobile_number", "restaurant__name"]
    readonly_fields = ["id", "created_at"]

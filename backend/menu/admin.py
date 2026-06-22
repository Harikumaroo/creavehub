"""
CraveHub — Menu Admin
"""

from django.contrib import admin
from .models import MenuCategory, MenuItem
from .services import MenuService


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ["name", "price", "discounted_price", "is_veg", "is_available", "calories"]
    show_change_link = True


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "restaurant", "display_order", "created_at"]
    list_filter = ["restaurant"]
    search_fields = ["name", "restaurant__name"]
    ordering = ["restaurant", "display_order"]
    inlines = [MenuItemInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        MenuService.invalidate_menu_cache(str(obj.restaurant_id))

    def delete_model(self, request, obj):
        restaurant_id = str(obj.restaurant_id)
        super().delete_model(request, obj)
        MenuService.invalidate_menu_cache(restaurant_id)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        "name", "restaurant", "category", "price",
        "discounted_price", "is_veg", "is_available", "calories",
    ]
    list_filter = ["is_veg", "is_available", "restaurant"]
    search_fields = ["name", "restaurant__name"]
    list_editable = ["is_available", "price", "discounted_price"]
    list_per_page = 50

    @admin.action(description="Mark selected items as available")
    def make_available(self, request, queryset):
        restaurant_ids = set(queryset.values_list("restaurant_id", flat=True))
        queryset.update(is_available=True)
        for rid in restaurant_ids:
            MenuService.invalidate_menu_cache(str(rid))

    @admin.action(description="Mark selected items as unavailable")
    def make_unavailable(self, request, queryset):
        restaurant_ids = set(queryset.values_list("restaurant_id", flat=True))
        queryset.update(is_available=False)
        for rid in restaurant_ids:
            MenuService.invalidate_menu_cache(str(rid))

    actions = [make_available, make_unavailable]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        MenuService.invalidate_menu_cache(str(obj.restaurant_id))
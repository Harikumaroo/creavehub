from django.contrib import admin
from .models import RestaurantReview, MenuItemReview

@admin.register(RestaurantReview)
class RestaurantReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "restaurant", "rating", "is_visible", "created_at"]
    list_filter  = ["rating", "is_visible"]
    search_fields = ["user__mobile_number", "restaurant__name"]
    list_editable = ["is_visible"]

@admin.register(MenuItemReview)
class MenuItemReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "menu_item", "rating", "is_visible", "created_at"]
    list_filter  = ["rating", "is_visible"]
    search_fields = ["user__mobile_number", "menu_item__name"]
    list_editable = ["is_visible"]

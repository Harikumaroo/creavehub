from django.contrib import admin
from .models import InstamartCategory, InstamartStore, InstamartProduct


@admin.register(InstamartCategory)
class InstamartCategoryAdmin(admin.ModelAdmin):
    list_display  = ["name", "display_order", "is_active"]
    list_editable = ["display_order", "is_active"]
    search_fields = ["name"]
    ordering      = ["display_order"]


@admin.register(InstamartStore)
class InstamartStoreAdmin(admin.ModelAdmin):
    list_display  = ["name", "city", "is_open", "is_active", "delivery_time", "delivery_fee"]
    list_filter   = ["city", "is_open", "is_active"]
    search_fields = ["name", "city", "pincode"]
    list_editable = ["is_open", "is_active"]
    readonly_fields = ["id", "created_at", "updated_at"]


class InstamartProductInline(admin.TabularInline):
    model   = InstamartProduct
    extra   = 0
    fields  = ["name", "brand", "price", "discount_price", "unit", "stock", "is_available"]
    show_change_link = True


@admin.register(InstamartProduct)
class InstamartProductAdmin(admin.ModelAdmin):
    list_display  = [
        "name", "brand", "store", "category",
        "price", "discount_price", "unit",
        "stock", "is_available", "is_featured",
    ]
    list_filter   = ["is_available", "is_featured", "store", "category"]
    search_fields = ["name", "brand", "store__name"]
    list_editable = ["is_available", "is_featured", "stock"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering      = ["store", "name"]
    list_per_page = 50

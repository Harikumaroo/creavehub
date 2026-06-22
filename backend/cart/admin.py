"""
CraveHub — Cart Admin (Phase 2)
"""

from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["price_at_purchase", "line_total", "created_at"]
    fields = ["menu_item", "quantity", "price_at_purchase", "line_total", "created_at"]

    def line_total(self, obj):
        return f"₹{obj.line_total}"
    line_total.short_description = "Line Total"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "item_count", "cart_subtotal", "created_at", "updated_at"]
    search_fields = ["user__email", "user__phone_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [CartItemInline]
    list_per_page = 25

    def item_count(self, obj):
        return obj.cart_items.count()
    item_count.short_description = "Items"

    def cart_subtotal(self, obj):
        return f"₹{obj.subtotal}"
    cart_subtotal.short_description = "Subtotal"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        "id", "cart", "menu_item", "quantity",
        "price_at_purchase", "cart_line_total", "created_at",
    ]
    search_fields = ["cart__user__email", "menu_item__name"]
    list_filter = ["created_at"]
    readonly_fields = ["id", "price_at_purchase", "created_at", "updated_at"]
    list_per_page = 30

    def cart_line_total(self, obj):
        return f"₹{obj.line_total}"
    cart_line_total.short_description = "Line Total"

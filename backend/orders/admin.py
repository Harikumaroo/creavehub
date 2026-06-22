"""
CraveHub — Orders Admin (Phase 3)
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["name", "price_at_purchase", "quantity", "is_veg", "line_total"]
    fields = ["menu_item", "name", "price_at_purchase", "quantity", "is_veg", "line_total"]

    def line_total(self, obj):
        return f"₹{obj.line_total}"
    line_total.short_description = "Total"


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ["status", "note", "changed_by", "created_at"]
    fields = ["status", "note", "changed_by", "created_at"]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id", "user", "restaurant", "status",
        "payment_status", "payment_method",
        "grand_total_display", "created_at",
    ]
    list_filter = ["status", "payment_status", "payment_method", "created_at"]
    search_fields = [
        "user__mobile_number", "user__full_name",
        "restaurant__name", "razorpay_order_id",
    ]
    readonly_fields = [
        "id", "subtotal", "delivery_fee", "tax", "grand_total",
        "razorpay_order_id", "razorpay_payment_id",
        "created_at", "updated_at", "delivered_at", "cancelled_at",
    ]
    ordering = ["-created_at"]
    list_per_page = 30
    inlines = [OrderItemInline, OrderStatusHistoryInline]

    fieldsets = (
        ("Order Info",   {"fields": ("id", "user", "restaurant", "instructions")}),
        ("Status",       {"fields": ("status", "payment_status", "payment_method")}),
        ("Pricing",      {"fields": ("subtotal", "delivery_fee", "tax", "grand_total")}),
        ("Delivery",     {"fields": (
            "delivery_address", "delivery_city", "delivery_pincode",
            "estimated_delivery_time", "delivered_at",
        )}),
        ("Cancellation", {"fields": ("cancelled_at", "cancel_reason")}),
        ("Payment Ref",  {"fields": ("razorpay_order_id", "razorpay_payment_id")}),
        ("Timestamps",   {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def grand_total_display(self, obj):
        return f"₹{obj.grand_total}"
    grand_total_display.short_description = "Grand Total"

    @admin.action(description="Mark selected orders as Confirmed")
    def confirm_orders(self, request, queryset):
        from .services import OrderService
        for order in queryset.filter(status=Order.Status.PENDING):
            OrderService.update_order_status(
                str(order.id), Order.Status.CONFIRMED, changed_by=request.user
            )
        self.message_user(request, "Selected orders confirmed.")

    actions = [confirm_orders]

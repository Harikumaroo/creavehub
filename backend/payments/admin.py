from django.contrib import admin
from .models import Payment, SavedPaymentMethod

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "order", "razorpay_order_id", "amount", "status", "created_at"]
    list_filter  = ["status", "currency"]
    search_fields = ["user__mobile_number", "razorpay_order_id", "razorpay_payment_id"]
    readonly_fields = ["id", "razorpay_order_id", "razorpay_payment_id", "razorpay_signature", "gateway_response", "created_at", "updated_at"]
    ordering = ["-created_at"]


@admin.register(SavedPaymentMethod)
class SavedPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["user", "provider", "card_type", "last_four", "is_default"]
    list_filter = ["provider", "card_type", "is_default"]
    search_fields = ["user__mobile_number", "provider", "last_four"]
    readonly_fields = ["id", "created_at", "updated_at"]

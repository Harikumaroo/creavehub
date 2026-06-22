"""
CraveHub — Payments Models (Phase 3)
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class Payment(BaseModel):

    class Status(models.TextChoices):
        CREATED   = "created",   "Created"
        ATTEMPTED = "attempted", "Attempted"
        PAID      = "paid",      "Paid"
        FAILED    = "failed",    "Failed"
        REFUNDED  = "refunded",  "Refunded"

    user   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
        db_index=True,
    )
    order  = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payment",
        db_index=True,
    )

    # Razorpay fields
    razorpay_order_id   = models.CharField(max_length=100, unique=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default="")
    razorpay_signature  = models.CharField(max_length=256, blank=True, default="")

    amount   = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status   = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.CREATED, db_index=True,
    )

    # Store full Razorpay webhook payload for audit
    gateway_response = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"], name="idx_payment_user_status"),
        ]

    def __str__(self):
        return f"Payment {self.razorpay_order_id} — {self.status}"


class SavedPaymentMethod(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_payment_methods",
        db_index=True,
    )
    provider = models.CharField(max_length=50, help_text="e.g. Visa, Mastercard, Paytm")
    card_type = models.CharField(max_length=20, blank=True, help_text="e.g. Credit, Debit, Wallet")
    last_four = models.CharField(max_length=4, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "saved_payment_methods"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.provider} **** {self.last_four} ({self.user})"

    def save(self, *args, **kwargs):
        if self.is_default:
            SavedPaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

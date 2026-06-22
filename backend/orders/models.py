"""
CraveHub — Orders Models (Phase 3)
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel
from restaurants.models import Restaurant
from menu.models import MenuItem


class Order(BaseModel):

    class Status(models.TextChoices):
        PENDING         = "pending",          "Pending"
        CONFIRMED       = "confirmed",        "Confirmed"
        PREPARING       = "preparing",        "Preparing"
        OUT_FOR_DELIVERY = "out_for_delivery","Out for Delivery"
        DELIVERED       = "delivered",        "Delivered"
        CANCELLED       = "cancelled",        "Cancelled"
        FAILED          = "failed",           "Failed"

    class PaymentStatus(models.TextChoices):
        PENDING   = "pending",   "Pending"
        PAID      = "paid",      "Paid"
        FAILED    = "failed",    "Failed"
        REFUNDED  = "refunded",  "Refunded"

    class PaymentMethod(models.TextChoices):
        RAZORPAY = "razorpay", "Razorpay"
        COD      = "cod",      "Cash on Delivery"
        WALLET   = "wallet",   "Wallet"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=True,
    )

    # Status
    status         = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.PENDING, db_index=True,
    )
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING, db_index=True,
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
    )

    # Pricing (all snapshotted at order time)
    subtotal      = models.DecimalField(max_digits=10, decimal_places=2)
    discount      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee  = models.DecimalField(max_digits=6,  decimal_places=2, default=0)
    tax           = models.DecimalField(max_digits=8,  decimal_places=2, default=0)
    grand_total   = models.DecimalField(max_digits=10, decimal_places=2)

    # Delivery address (snapshot — user may change address later)
    delivery_address = models.TextField()
    delivery_city    = models.CharField(max_length=100, blank=True)
    delivery_pincode = models.CharField(max_length=10, blank=True)

    # Tracking
    estimated_delivery_time = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Minutes"
    )
    delivered_at  = models.DateTimeField(null=True, blank=True)
    cancelled_at  = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True, default="")

    # Special instructions from user
    instructions = models.TextField(blank=True, default="")

    # Razorpay reference (populated after payment)
    razorpay_order_id   = models.CharField(max_length=100, blank=True, default="")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "orders"
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"],          name="idx_order_user_status"),
            models.Index(fields=["restaurant", "status"],    name="idx_order_rest_status"),
            models.Index(fields=["status", "payment_status"],name="idx_order_status_pay"),
            models.Index(fields=["created_at"],              name="idx_order_created"),
        ]

    def __str__(self):
        return f"Order {self.id} — {self.user} — {self.status}"

    @property
    def is_cancellable(self) -> bool:
        return self.status in (self.Status.PENDING, self.Status.CONFIRMED)


class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    name              = models.CharField(max_length=200)   # snapshot
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)
    quantity          = models.PositiveSmallIntegerField()
    is_veg            = models.BooleanField(default=True)

    class Meta:
        db_table = "order_items"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        indexes = [
            models.Index(fields=["order"], name="idx_orderitem_order"),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.name}"

    @property
    def line_total(self):
        return self.price_at_purchase * self.quantity


class OrderStatusHistory(BaseModel):
    """
    Immutable log of every status change on an order.
    Powers the live tracking timeline.
    """
    order      = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="status_history", db_index=True,
    )
    status     = models.CharField(max_length=20, choices=Order.Status.choices)
    note       = models.TextField(blank=True, default="")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    class Meta:
        db_table = "order_status_history"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["order", "created_at"], name="idx_orderhist_order_ts"),
        ]

    def __str__(self):
        return f"Order {self.order_id} → {self.status}"

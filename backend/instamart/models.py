"""
CraveHub — Instamart Models
Quick commerce / grocery delivery module.
Mirrors the food ordering structure but scoped to grocery products.
"""

from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from core.models import BaseModel, SoftDeleteModel
from datetime import time as dt_time
from django.utils import timezone as django_tz


class InstamartCategory(BaseModel):
    name          = models.CharField(max_length=100, unique=True, db_index=True)
    image         = models.URLField(max_length=500, blank=True, default="")
    display_order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_active     = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "instamart_categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class InstamartStore(SoftDeleteModel):
    """
    A store/dark-store that fulfils Instamart orders.
    """
    name          = models.CharField(max_length=200, db_index=True)
    address       = models.TextField()
    city          = models.CharField(max_length=100, db_index=True)
    pincode       = models.CharField(max_length=10)
    latitude      = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_time = models.PositiveSmallIntegerField(default=15, help_text="Minutes")
    delivery_fee  = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    minimum_order = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_open       = models.BooleanField(default=True, db_index=True)
    is_active     = models.BooleanField(default=True, db_index=True)
    image         = models.URLField(max_length=500, blank=True, default="")

    # ── Operating Hours ─────────────────────────────────────────
    opening_time = models.TimeField(
        default=dt_time(0, 0),
        help_text="Daily opening time (HH:MM). Use 00:00 for midnight-start.",
    )
    closing_time = models.TimeField(
        default=dt_time(23, 59),
        help_text="Daily closing time (HH:MM). Use 23:59 for end-of-day.",
    )
    is_24hrs = models.BooleanField(
        default=True, db_index=True,
        help_text="If True, opening/closing times are ignored and the restaurant is always open.",
    )

    # ── Time-based helpers ──────────────────────────────────────
    def is_open_at(self, check_time) -> bool:
        if self.is_24hrs:
            return True
        if not self.is_open:
            return False
        if self.opening_time <= self.closing_time:
            return self.opening_time <= check_time <= self.closing_time
        else:
            return check_time >= self.opening_time or check_time <= self.closing_time

    @property
    def is_currently_open(self) -> bool:
        if not self.is_open or not self.is_active:
            return False
        now = django_tz.localtime().time()
        return self.is_open_at(now)

    @property
    def is_midnight_store(self) -> bool:
        if self.is_24hrs:
            return False
        return self.opening_time > self.closing_time

    @property
    def formatted_hours(self) -> str:
        if self.is_24hrs:
            return "Open 24 hours"
        return (
            f"{self.opening_time.strftime('%I:%M %p')} – "
            f"{self.closing_time.strftime('%I:%M %p')}"
        )

    class Meta:
        db_table = "instamart_stores"
        ordering = ["name"]
        indexes  = [
            models.Index(fields=["city", "is_active", "is_open"], name="idx_istore_city"),
        ]

    def __str__(self):
        return self.name


class InstamartProduct(BaseModel):
    """
    A grocery/FMCG product sold via Instamart.
    """
    store         = models.ForeignKey(
        InstamartStore,
        on_delete=models.CASCADE,
        related_name="products",
        db_index=True,
    )
    category      = models.ForeignKey(
        InstamartCategory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products",
        db_index=True,
    )
    name          = models.CharField(max_length=255, db_index=True)
    description   = models.TextField(blank=True, default="")
    brand         = models.CharField(max_length=100, blank=True, default="")
    image         = models.URLField(max_length=500, blank=True, default="")
    price         = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    unit          = models.CharField(max_length=50, default="1 unit")  # e.g. "500g", "1 L"
    stock         = models.PositiveIntegerField(default=0)
    is_available  = models.BooleanField(default=True, db_index=True)
    is_featured   = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "instamart_products"
        ordering = ["name"]
        indexes  = [
            models.Index(fields=["store", "is_available"],      name="idx_iprod_store_avail"),
            models.Index(fields=["category", "is_available"],   name="idx_iprod_cat_avail"),
            models.Index(fields=["name"],                       name="idx_iprod_name"),
        ]

    def __str__(self):
        return f"{self.name} ({self.store.name})"

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def has_discount(self):
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0 and self.is_available

    @property
    def stock_status(self) -> str:
        if not self.is_available or self.stock <= 0:
            return "sold_out"
        return "available"


class InstamartOrder(BaseModel):
    class Status(models.TextChoices):
        PENDING         = "pending",          "Pending"
        CONFIRMED       = "confirmed",        "Confirmed"
        PREPARING       = "preparing",        "Preparing"
        OUT_FOR_DELIVERY = "out_for_delivery","Out for Delivery"
        DELIVERED       = "delivered",        "Delivered"
        CANCELLED       = "cancelled",        "Cancelled"
        FAILED          = "failed",           "Failed"

    class PaymentMethod(models.TextChoices):
        RAZORPAY = "razorpay", "Razorpay"
        COD      = "cod",      "Cash on Delivery"
        WALLET   = "wallet",   "Wallet"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="instamart_orders",
        db_index=True,
    )
    store = models.ForeignKey(
        InstamartStore,
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=True,
    )
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    
    subtotal      = models.DecimalField(max_digits=10, decimal_places=2)
    discount      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee  = models.DecimalField(max_digits=6,  decimal_places=2, default=0)
    tax           = models.DecimalField(max_digits=8,  decimal_places=2, default=0)
    grand_total   = models.DecimalField(max_digits=10, decimal_places=2)
    
    delivery_address = models.TextField()
    
    # Gift Checkout Fields
    is_gift = models.BooleanField(default=False, db_index=True)
    recipient_name = models.CharField(max_length=200, blank=True, default="")
    recipient_mobile = models.CharField(max_length=20, blank=True, default="")
    recipient_email = models.EmailField(blank=True, null=True)
    gift_message = models.TextField(blank=True, default="")
    delivery_schedule_type = models.CharField(max_length=20, default="now")
    scheduled_delivery_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "instamart_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Instamart Order {self.id} — {self.status}"


class InstamartOrderItem(BaseModel):
    order = models.ForeignKey(
        InstamartOrder,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    product = models.ForeignKey(
        InstamartProduct,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    name              = models.CharField(max_length=255)
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)
    quantity          = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "instamart_order_items"

    def __str__(self):
        return f"{self.quantity}x {self.name}"

class InstamartCart(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instamart_cart",
        db_index=True,
    )
    
    class Meta:
        db_table = "instamart_carts"
        
    def __str__(self):
        return f"Instamart Cart of {self.user}"

class InstamartCartItem(BaseModel):
    cart = models.ForeignKey(
        InstamartCart,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    product = models.ForeignKey(
        InstamartProduct,
        on_delete=models.CASCADE,
        related_name="cart_items",
        db_index=True,
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "instamart_cart_items"
        unique_together = [("cart", "product")]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

"""
CraveHub — Offers Models
"""

from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from core.models import BaseModel
from core.validators import validate_percentage


class DiscountType(models.TextChoices):
    PERCENTAGE = "PERCENTAGE", "Percentage"
    FLAT = "FLAT", "Flat Amount"
    FREE_DELIVERY = "FREE_DELIVERY", "Free Delivery"


class OfferQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, expiry_date__gte=timezone.now().date())


class OfferManager(models.Manager):
    def get_queryset(self):
        return OfferQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class Offer(BaseModel):
    title = models.CharField(max_length=200)
    coupon_code = models.CharField(max_length=30, unique=True, db_index=True)
    discount_type = models.CharField(
        max_length=20, choices=DiscountType.choices,
        default=DiscountType.FLAT, db_index=True,
    )
    discount_value = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],
    )
    minimum_order_amount = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    maximum_discount = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))],
    )
    expiry_date = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    restaurants = models.ManyToManyField("restaurants.Restaurant", related_name="offers", blank=True)

    objects = OfferManager()

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "expiry_date"], name="idx_offer_active_expiry"),
            models.Index(fields=["coupon_code"], name="idx_offer_coupon"),
        ]

    def __str__(self):
        return f"{self.coupon_code} — {self.title}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.discount_type == DiscountType.PERCENTAGE:
            try:
                validate_percentage(float(self.discount_value))
            except Exception:
                raise ValidationError(
                    {"discount_value": "Percentage discount must be between 0 and 100."}
                )

    @property
    def is_expired(self) -> bool:
        return self.expiry_date < timezone.now().date()


class SavedOffer(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_offers",
        db_index=True,
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )

    class Meta:
        db_table = "saved_offers"
        unique_together = ["user", "offer"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.offer.coupon_code}"
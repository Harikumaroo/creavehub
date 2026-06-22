"""
CraveHub — Restaurants Models
"""

from datetime import time as dt_time

from django.conf import settings
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone as django_tz
from django.utils.text import slugify
from categories.models import Category
from core.models import BaseModel, SoftDeleteModel
from core.validators import validate_latitude, validate_longitude, validate_pincode


class Restaurant(SoftDeleteModel):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True, default="")
    logo = models.URLField(max_length=500, blank=True, default="")
    cover_image = models.URLField(max_length=500, blank=True, default="")
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0.0,
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('5.0'))],
        db_index=True,
    )
    total_reviews = models.PositiveIntegerField(default=0)
    average_delivery_time = models.PositiveSmallIntegerField(default=30)
    minimum_order_amount = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    is_pure_veg = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    delivery_fee = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    is_open = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    preparation_time = models.PositiveSmallIntegerField(default=15)

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

    class RestaurantType(models.TextChoices):
        FOOD = "food", "Food Ordering"
        INSTAMART = "instamart", "Instamart"
        DINING = "dining", "Dining"

    restaurant_type = models.CharField(
        max_length=20,
        choices=RestaurantType.choices,
        default=RestaurantType.FOOD,
        db_index=True,
    )

    # ── Time-based helpers ──────────────────────────────────────
    def is_open_at(self, check_time) -> bool:
        """
        Return True if the restaurant operates at *check_time*.
        Handles overnight ranges like 22:00 → 06:00 (midnight restaurants).
        """
        if self.is_24hrs:
            return True
        if not self.is_open:
            return False
        if self.opening_time <= self.closing_time:
            # Normal range, e.g. 09:00 → 23:00
            return self.opening_time <= check_time <= self.closing_time
        else:
            # Overnight range, e.g. 22:00 → 06:00
            return check_time >= self.opening_time or check_time <= self.closing_time

    @property
    def is_currently_open(self) -> bool:
        """Check against the current server-local time."""
        if not self.is_open or not self.is_active:
            return False
        now = django_tz.localtime().time()
        return self.is_open_at(now)

    @property
    def is_midnight_restaurant(self) -> bool:
        """True when operating hours span midnight (opening > closing)."""
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
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"
        ordering = ["-rating", "name"]
        indexes = [
            models.Index(
                fields=["is_active", "is_deleted", "rating"],
                name="idx_rest_active_rating",
            ),
            models.Index(fields=["is_active", "is_pure_veg"], name="idx_rest_veg"),
            models.Index(fields=["slug"], name="idx_rest_slug"),
            models.Index(fields=["is_open", "is_active"], name="idx_rest_open_active"),
            models.Index(fields=["restaurant_type", "is_active"], name="idx_rest_type"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.name)
        slug, counter = base_slug, 1
        qs = Restaurant.all_objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            qs = Restaurant.all_objects.filter(slug=slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
        return slug


class RestaurantAddress(BaseModel):
    restaurant = models.OneToOneField(
        Restaurant, on_delete=models.CASCADE, related_name="address",
    )
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=10, validators=[validate_pincode])
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[validate_latitude],
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[validate_longitude],
    )

    class Meta:
        verbose_name = "Restaurant Address"
        verbose_name_plural = "Restaurant Addresses"
        indexes = [
            models.Index(fields=["city"], name="idx_addr_city"),
            models.Index(fields=["pincode"], name="idx_addr_pincode"),
        ]

    def __str__(self):
        return f"{self.restaurant.name} — {self.city}"


class RestaurantCategory(BaseModel):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="restaurant_categories",
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="restaurant_categories",
    )

    class Meta:
        verbose_name = "Restaurant Category"
        verbose_name_plural = "Restaurant Categories"
        unique_together = [("restaurant", "category")]
        indexes = [
            models.Index(
                fields=["restaurant", "category"],
                name="idx_restcat_rest_cat",
            ),
        ]

    def __str__(self):
        return f"{self.restaurant.name} → {self.category.name}"


class FavoriteRestaurant(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_restaurants",
        db_index=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )

    class Meta:
        db_table = "favorite_restaurants"
        unique_together = ["user", "restaurant"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.restaurant.name}"
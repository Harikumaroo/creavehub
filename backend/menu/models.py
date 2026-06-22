"""
CraveHub — Menu Models
"""

from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from restaurants.models import Restaurant
from core.models import BaseModel


class MenuCategory(BaseModel):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE,
        related_name="menu_categories", db_index=True,
    )
    name = models.CharField(max_length=150)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ["display_order", "name"]
        unique_together = [("restaurant", "name")]
        indexes = [
            models.Index(
                fields=["restaurant", "display_order"],
                name="idx_menucat_rest_order",
            )
        ]

    def __str__(self):
        return f"{self.restaurant.name} — {self.name}"


class MenuItem(BaseModel):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE,
        related_name="menu_items", db_index=True,
    )
    category = models.ForeignKey(
        MenuCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="items",
    )
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, default="")
    image = models.URLField(max_length=500, blank=True, default="")
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],
    )
    discounted_price = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))],
    )
    is_veg = models.BooleanField(default=True, db_index=True)
    is_available = models.BooleanField(default=True, db_index=True)
    is_in_stock = models.BooleanField(
        default=True, db_index=True,
        help_text="Real-time stock status. False = sold out.",
    )
    calories = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ["category__display_order", "name"]
        indexes = [
            models.Index(fields=["restaurant", "is_available"], name="idx_item_rest_avail"),
            models.Index(fields=["restaurant", "category"], name="idx_item_rest_cat"),
            models.Index(fields=["is_veg", "is_available"], name="idx_item_veg_avail"),
        ]

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

    @property
    def effective_price(self):
        return self.discounted_price if self.discounted_price is not None else self.price

    @property
    def has_discount(self) -> bool:
        return self.discounted_price is not None and self.discounted_price < self.price

    @property
    def stock_status(self) -> str:
        if not self.is_available or not self.is_in_stock:
            return "sold_out"
        return "available"


class FavoriteMenuItem(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_menu_items",
        db_index=True,
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )

    class Meta:
        db_table = "favorite_menu_items"
        unique_together = ["user", "menu_item"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.menu_item.name}"
"""
CraveHub — Reviews Models (Phase 3)
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from core.models import BaseModel
from restaurants.models import Restaurant
from menu.models import MenuItem
from orders.models import Order


class RestaurantReview(BaseModel):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="restaurant_reviews", db_index=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews", db_index=True)
    order      = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="restaurant_review")
    rating     = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], db_index=True)
    comment    = models.TextField(blank=True, default="")
    is_visible = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "restaurant_reviews"
        unique_together = [("user", "restaurant")]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["restaurant", "is_visible", "rating"], name="idx_rev_rest_vis_rat"),
        ]

    def __str__(self):
        return f"{self.user} → {self.restaurant.name} ({self.rating}★)"


class MenuItemReview(BaseModel):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="item_reviews", db_index=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="reviews", db_index=True)
    order     = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="item_reviews")
    rating    = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment   = models.TextField(blank=True, default="")
    is_visible = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "menu_item_reviews"
        unique_together = [("user", "menu_item")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} → {self.menu_item.name} ({self.rating}★)"

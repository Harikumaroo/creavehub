"""
CraveHub — AI Engine Models
Stores recommendation logs and user preference profiles.
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class UserPreferenceProfile(BaseModel):
    """
    Auto-built preference profile per user.
    Updated after each order and review.
    """
    user             = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preference_profile",
        db_index=True,
    )
    prefers_veg      = models.BooleanField(default=False)
    favourite_cuisines = models.JSONField(default=list, blank=True)   # ["biryani", "pizza"]
    favourite_categories = models.JSONField(default=list, blank=True) # [uuid, uuid]
    avg_order_value  = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_orders     = models.PositiveIntegerField(default=0)
    # Raw embedding vector (future use with pgvector / Pinecone)
    embedding        = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "user_preference_profiles"

    def __str__(self):
        return f"Profile of {self.user}"


class AIRecommendationLog(BaseModel):
    """
    Audit log of every recommendation served — for model evaluation.
    """
    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="recommendation_logs",
        db_index=True,
    )
    context      = models.CharField(max_length=50, default="home")  # home / search / post_order
    prompt_hash  = models.CharField(max_length=64, blank=True)
    model_used   = models.CharField(max_length=50, default="rule_based")
    # Snapshot of what was recommended
    recommended_restaurant_ids = models.JSONField(default=list, blank=True)
    recommended_item_ids       = models.JSONField(default=list, blank=True)
    latency_ms   = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "ai_recommendation_logs"
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["user", "context"], name="idx_ai_user_context"),
        ]

    def __str__(self):
        return f"Reco log {self.id} [{self.context}]"

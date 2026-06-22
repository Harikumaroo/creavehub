"""
CraveHub — Search Models
Stores search history per user for personalised suggestions.
"""

from django.conf import settings
from django.db import models
from core.models import BaseModel


class SearchHistory(BaseModel):
    user  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="search_history",
        db_index=True,
    )
    query = models.CharField(max_length=200, db_index=True)

    class Meta:
        db_table = "search_history"
        ordering = ["-created_at"]
        # Keep only the latest entry per user+query
        unique_together = [("user", "query")]
        indexes = [
            models.Index(fields=["user", "created_at"], name="idx_search_user_ts"),
        ]

    def __str__(self):
        return f"{self.user} → '{self.query}'"

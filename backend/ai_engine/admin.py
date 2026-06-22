from django.contrib import admin
from .models import UserPreferenceProfile, AIRecommendationLog


@admin.register(UserPreferenceProfile)
class UserPreferenceProfileAdmin(admin.ModelAdmin):
    list_display  = ["user", "prefers_veg", "total_orders", "avg_order_value", "updated_at"]
    search_fields = ["user__mobile_number", "user__full_name"]
    readonly_fields = ["id", "embedding", "created_at", "updated_at"]


@admin.register(AIRecommendationLog)
class AIRecommendationLogAdmin(admin.ModelAdmin):
    list_display  = ["id", "user", "context", "model_used", "latency_ms", "created_at"]
    list_filter   = ["context", "model_used"]
    search_fields = ["user__mobile_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering      = ["-created_at"]

import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="UserPreferenceProfile",
            fields=[
                ("id",                   models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",           models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",           models.DateTimeField(auto_now=True)),
                ("user",                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="preference_profile", to=settings.AUTH_USER_MODEL)),
                ("prefers_veg",          models.BooleanField(default=False)),
                ("favourite_cuisines",   models.JSONField(blank=True, default=list)),
                ("favourite_categories", models.JSONField(blank=True, default=list)),
                ("avg_order_value",      models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("total_orders",         models.PositiveIntegerField(default=0)),
                ("embedding",            models.JSONField(blank=True, default=list)),
            ],
            options={"db_table": "user_preference_profiles"},
        ),
        migrations.CreateModel(
            name="AIRecommendationLog",
            fields=[
                ("id",                          models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",                  models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",                  models.DateTimeField(auto_now=True)),
                ("user",                        models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="recommendation_logs", to=settings.AUTH_USER_MODEL)),
                ("context",                     models.CharField(default="home", max_length=50)),
                ("prompt_hash",                 models.CharField(blank=True, max_length=64)),
                ("model_used",                  models.CharField(default="rule_based", max_length=50)),
                ("recommended_restaurant_ids",  models.JSONField(blank=True, default=list)),
                ("recommended_item_ids",        models.JSONField(blank=True, default=list)),
                ("latency_ms",                  models.PositiveIntegerField(default=0)),
            ],
            options={"db_table": "ai_recommendation_logs", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="airecommendationlog", index=models.Index(fields=["user","context"], name="idx_ai_user_context")),
    ]

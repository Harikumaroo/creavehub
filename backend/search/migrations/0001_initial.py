import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="SearchHistory",
            fields=[
                ("id",         models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user",       models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="search_history", to=settings.AUTH_USER_MODEL)),
                ("query",      models.CharField(db_index=True, max_length=200)),
            ],
            options={"db_table": "search_history", "ordering": ["-created_at"]},
        ),
        migrations.AlterUniqueTogether(name="searchhistory", unique_together={("user","query")}),
        migrations.AddIndex(model_name="searchhistory", index=models.Index(fields=["user","created_at"], name="idx_search_user_ts")),
    ]

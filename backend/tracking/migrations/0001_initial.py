import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("orders", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="DeliveryAgent",
            fields=[
                ("id",               models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",       models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",       models.DateTimeField(auto_now=True)),
                ("user",             models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="delivery_agent", to=settings.AUTH_USER_MODEL)),
                ("full_name",        models.CharField(max_length=200)),
                ("phone",            models.CharField(max_length=15)),
                ("vehicle_type",     models.CharField(default="bike", max_length=50)),
                ("vehicle_number",   models.CharField(blank=True, default="", max_length=20)),
                ("status",           models.CharField(choices=[("available","Available"),("on_delivery","On Delivery"),("offline","Offline")], db_index=True, default="offline", max_length=20)),
                ("current_latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("current_longitude",models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("last_location_at", models.DateTimeField(blank=True, null=True)),
                ("is_active",        models.BooleanField(db_index=True, default=True)),
            ],
            options={"db_table": "delivery_agents"},
        ),
        migrations.CreateModel(
            name="OrderTracking",
            fields=[
                ("id",               models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",       models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",       models.DateTimeField(auto_now=True)),
                ("order",            models.OneToOneField(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="tracking", to="orders.order")),
                ("agent",            models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="active_deliveries", to="tracking.deliveryagent")),
                ("agent_latitude",   models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("agent_longitude",  models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("dest_latitude",    models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("dest_longitude",   models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("eta_minutes",      models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
            options={"db_table": "order_tracking"},
        ),
        migrations.CreateModel(
            name="LocationPing",
            fields=[
                ("id",        models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",models.DateTimeField(auto_now=True)),
                ("tracking",  models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="pings", to="tracking.ordertracking")),
                ("latitude",  models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
            ],
            options={"db_table": "location_pings", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="deliveryagent", index=models.Index(fields=["status","is_active"],       name="idx_agent_status")),
        migrations.AddIndex(model_name="locationping",  index=models.Index(fields=["tracking","created_at"],   name="idx_ping_tracking_ts")),
    ]

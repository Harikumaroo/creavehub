import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id",          models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",  models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",  models.DateTimeField(auto_now=True)),
                ("user",        models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
                ("title",       models.CharField(max_length=200)),
                ("body",        models.TextField()),
                ("notif_type",  models.CharField(choices=[("order_placed","Order Placed"),("order_confirmed","Order Confirmed"),("order_preparing","Order Preparing"),("order_out_delivery","Out for Delivery"),("order_delivered","Order Delivered"),("order_cancelled","Order Cancelled"),("payment_success","Payment Successful"),("payment_failed","Payment Failed"),("offer_alert","Offer Alert"),("review_request","Review Request"),("system","System")], db_index=True, default="system", max_length=30)),
                ("is_read",     models.BooleanField(db_index=True, default=False)),
                ("metadata",    models.JSONField(blank=True, default=dict)),
            ],
            options={"db_table": "notifications", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PushToken",
            fields=[
                ("id",          models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",  models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",  models.DateTimeField(auto_now=True)),
                ("user",        models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="push_tokens", to=settings.AUTH_USER_MODEL)),
                ("token",       models.TextField(unique=True)),
                ("platform",    models.CharField(choices=[("android","Android"),("ios","iOS"),("web","Web")], default="android", max_length=10)),
                ("is_active",   models.BooleanField(default=True)),
            ],
            options={"db_table": "push_tokens"},
        ),
        migrations.AddIndex(model_name="notification", index=models.Index(fields=["user","is_read"],    name="idx_notif_user_read")),
        migrations.AddIndex(model_name="notification", index=models.Index(fields=["user","notif_type"], name="idx_notif_user_type")),
        migrations.AddIndex(model_name="pushtoken",    index=models.Index(fields=["user","is_active"],  name="idx_push_user_active")),
    ]

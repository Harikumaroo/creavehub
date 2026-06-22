import uuid
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="InstamartCategory",
            fields=[
                ("id",            models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",    models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",    models.DateTimeField(auto_now=True)),
                ("name",          models.CharField(db_index=True, max_length=100, unique=True)),
                ("image",         models.URLField(blank=True, default="", max_length=500)),
                ("display_order", models.PositiveSmallIntegerField(db_index=True, default=0)),
                ("is_active",     models.BooleanField(db_index=True, default=True)),
            ],
            options={"db_table": "instamart_categories", "ordering": ["display_order","name"]},
        ),
        migrations.CreateModel(
            name="InstamartStore",
            fields=[
                ("id",            models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",    models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",    models.DateTimeField(auto_now=True)),
                ("is_deleted",    models.BooleanField(db_index=True, default=False)),
                ("deleted_at",    models.DateTimeField(blank=True, null=True)),
                ("name",          models.CharField(db_index=True, max_length=200)),
                ("address",       models.TextField()),
                ("city",          models.CharField(db_index=True, max_length=100)),
                ("pincode",       models.CharField(max_length=10)),
                ("latitude",      models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude",     models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("delivery_time", models.PositiveSmallIntegerField(default=15)),
                ("delivery_fee",  models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ("minimum_order", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("is_open",       models.BooleanField(db_index=True, default=True)),
                ("is_active",     models.BooleanField(db_index=True, default=True)),
                ("image",         models.URLField(blank=True, default="", max_length=500)),
            ],
            options={"db_table": "instamart_stores", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="InstamartProduct",
            fields=[
                ("id",             models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ("created_at",     models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at",     models.DateTimeField(auto_now=True)),
                ("store",          models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="products", to="instamart.instamartstore")),
                ("category",       models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="instamart.instamartcategory")),
                ("name",           models.CharField(db_index=True, max_length=255)),
                ("description",    models.TextField(blank=True, default="")),
                ("brand",          models.CharField(blank=True, default="", max_length=100)),
                ("image",          models.URLField(blank=True, default="", max_length=500)),
                ("price",          models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ("discount_price", models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ("unit",           models.CharField(default="1 unit", max_length=50)),
                ("stock",          models.PositiveIntegerField(default=0)),
                ("is_available",   models.BooleanField(db_index=True, default=True)),
                ("is_featured",    models.BooleanField(db_index=True, default=False)),
            ],
            options={"db_table": "instamart_products", "ordering": ["name"]},
        ),
        migrations.AddIndex(model_name="instamartstore",   index=models.Index(fields=["city","is_active","is_open"], name="idx_istore_city")),
        migrations.AddIndex(model_name="instamartproduct", index=models.Index(fields=["store","is_available"],       name="idx_iprod_store_avail")),
        migrations.AddIndex(model_name="instamartproduct", index=models.Index(fields=["category","is_available"],    name="idx_iprod_cat_avail")),
        migrations.AddIndex(model_name="instamartproduct", index=models.Index(fields=["name"],                       name="idx_iprod_name")),
    ]

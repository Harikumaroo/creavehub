import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menu', '0001_initial'),
        ('restaurants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='restaurants.restaurant')),
                ('status', models.CharField(choices=[('pending','Pending'),('confirmed','Confirmed'),('preparing','Preparing'),('out_for_delivery','Out for Delivery'),('delivered','Delivered'),('cancelled','Cancelled'),('failed','Failed')], db_index=True, default='pending', max_length=20)),
                ('payment_status', models.CharField(choices=[('pending','Pending'),('paid','Paid'),('failed','Failed'),('refunded','Refunded')], db_index=True, default='pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('razorpay','Razorpay'),('cod','Cash on Delivery'),('wallet','Wallet')], default='cod', max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delivery_fee', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('grand_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delivery_address', models.TextField()),
                ('delivery_city', models.CharField(blank=True, max_length=100)),
                ('delivery_pincode', models.CharField(blank=True, max_length=10)),
                ('estimated_delivery_time', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('cancel_reason', models.TextField(blank=True, default='')),
                ('instructions', models.TextField(blank=True, default='')),
                ('razorpay_order_id', models.CharField(blank=True, default='', max_length=100)),
                ('razorpay_payment_id', models.CharField(blank=True, default='', max_length=100)),
            ],
            options={'db_table': 'orders', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='menu.menuitem')),
                ('name', models.CharField(max_length=200)),
                ('price_at_purchase', models.DecimalField(decimal_places=2, max_digits=8)),
                ('quantity', models.PositiveSmallIntegerField()),
                ('is_veg', models.BooleanField(default=True)),
            ],
            options={'db_table': 'order_items', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderStatusHistory',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='orders.order')),
                ('status', models.CharField(choices=[('pending','Pending'),('confirmed','Confirmed'),('preparing','Preparing'),('out_for_delivery','Out for Delivery'),('delivered','Delivered'),('cancelled','Cancelled'),('failed','Failed')], max_length=20)),
                ('note', models.TextField(blank=True, default='')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'order_status_history', 'ordering': ['created_at']},
        ),
        migrations.AddIndex(model_name='order', index=models.Index(fields=['user','status'], name='idx_order_user_status')),
        migrations.AddIndex(model_name='order', index=models.Index(fields=['restaurant','status'], name='idx_order_rest_status')),
        migrations.AddIndex(model_name='order', index=models.Index(fields=['status','payment_status'], name='idx_order_status_pay')),
        migrations.AddIndex(model_name='order', index=models.Index(fields=['created_at'], name='idx_order_created')),
        migrations.AddIndex(model_name='orderitem', index=models.Index(fields=['order'], name='idx_orderitem_order')),
        migrations.AddIndex(model_name='orderstatushistory', index=models.Index(fields=['order','created_at'], name='idx_orderhist_order_ts')),
    ]

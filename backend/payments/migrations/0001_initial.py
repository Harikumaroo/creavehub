import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to=settings.AUTH_USER_MODEL)),
                ('order', models.OneToOneField(db_index=True, on_delete=django.db.models.deletion.PROTECT, related_name='payment', to='orders.order')),
                ('razorpay_order_id', models.CharField(db_index=True, max_length=100, unique=True)),
                ('razorpay_payment_id', models.CharField(blank=True, default='', max_length=100)),
                ('razorpay_signature', models.CharField(blank=True, default='', max_length=256)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='INR', max_length=10)),
                ('status', models.CharField(choices=[('created','Created'),('attempted','Attempted'),('paid','Paid'),('failed','Failed'),('refunded','Refunded')], db_index=True, default='created', max_length=20)),
                ('gateway_response', models.JSONField(blank=True, default=dict)),
            ],
            options={'db_table': 'payments', 'ordering': ['-created_at']},
        ),
        migrations.AddIndex(model_name='payment', index=models.Index(fields=['user','status'], name='idx_payment_user_status')),
    ]

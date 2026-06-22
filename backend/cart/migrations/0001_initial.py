# CraveHub — Cart initial migration (Phase 2)

import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menu', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(
                    db_index=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cart',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Cart',
                'verbose_name_plural': 'Carts',
                'db_table': 'carts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('price_at_purchase', models.DecimalField(decimal_places=2, max_digits=8)),
                ('cart', models.ForeignKey(
                    db_index=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cart_items',
                    to='cart.cart',
                )),
                ('menu_item', models.ForeignKey(
                    db_index=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cart_items',
                    to='menu.menuitem',
                )),
            ],
            options={
                'verbose_name': 'Cart Item',
                'verbose_name_plural': 'Cart Items',
                'db_table': 'cart_items',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('cart', 'menu_item')},
        ),
        migrations.AddIndex(
            model_name='cartitem',
            index=models.Index(fields=['cart', 'menu_item'], name='idx_cartitem_cart_item'),
        ),
    ]

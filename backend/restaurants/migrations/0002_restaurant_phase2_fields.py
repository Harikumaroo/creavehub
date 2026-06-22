# CraveHub — Phase 2: Add delivery_fee, is_open, is_featured, preparation_time, restaurant_type

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='delivery_fee',
            field=models.DecimalField(
                decimal_places=2, default=0.0, max_digits=6,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='is_open',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='is_featured',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='preparation_time',
            field=models.PositiveSmallIntegerField(default=15),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='restaurant_type',
            field=models.CharField(
                choices=[('food', 'Food Ordering'), ('instamart', 'Instamart'), ('dining', 'Dining')],
                db_index=True, default='food', max_length=20,
            ),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['is_open', 'is_active'], name='idx_rest_open_active'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['restaurant_type', 'is_active'], name='idx_rest_type'),
        ),
    ]

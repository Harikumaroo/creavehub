import uuid
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('menu', '0001_initial'),
        ('orders', '0001_initial'),
        ('restaurants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='RestaurantReview',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_reviews', to=settings.AUTH_USER_MODEL)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='restaurants.restaurant')),
                ('order', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='restaurant_review', to='orders.order')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], db_index=True)),
                ('comment', models.TextField(blank=True, default='')),
                ('is_visible', models.BooleanField(db_index=True, default=True)),
            ],
            options={'db_table': 'restaurant_reviews', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='MenuItemReview',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_reviews', to=settings.AUTH_USER_MODEL)),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='menu.menuitem')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_reviews', to='orders.order')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True, default='')),
                ('is_visible', models.BooleanField(db_index=True, default=True)),
            ],
            options={'db_table': 'menu_item_reviews', 'ordering': ['-created_at']},
        ),
        migrations.AlterUniqueTogether(name='restaurantreview', unique_together={('user','restaurant')}),
        migrations.AlterUniqueTogether(name='menuitemreview', unique_together={('user','menu_item')}),
        migrations.AddIndex(model_name='restaurantreview', index=models.Index(fields=['restaurant','is_visible','rating'], name='idx_rev_rest_vis_rat')),
    ]

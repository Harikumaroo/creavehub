import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from restaurants.models import Restaurant

# Set 7 AM to 10 PM
opening = datetime.time(7, 0)
closing = datetime.time(22, 0)

count = Restaurant.objects.update(
    opening_time=opening,
    closing_time=closing,
    is_24hrs=False
)

print(f"Successfully updated {count} restaurants to operate from 07:00 to 22:00.")

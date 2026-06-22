import os
import django
import sys

# Setup django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()

from core.models import AppSector

sectors = [
    {
        "name": "Food Delivery",
        "emoji": "🍔",
        "bg_gradient_start": "#FFF0E6",
        "bg_gradient_end": "#FFE4CC",
        "border_color": "#F5C9A0",
        "route": "/",
        "display_order": 1,
    },
    {
        "name": "Instamart",
        "emoji": "🛒",
        "bg_gradient_start": "#E6F5EC",
        "bg_gradient_end": "#CCECD8",
        "border_color": "#A0D8B6",
        "route": "/instamart",
        "display_order": 2,
    },
    {
        "name": "Dining Out",
        "emoji": "🍽️",
        "bg_gradient_start": "#F0E6FF",
        "bg_gradient_end": "#E4CCFF",
        "border_color": "#C9A0F5",
        "route": "/dining",
        "display_order": 3,
    },
    {
        "name": "Party Orders",
        "emoji": "🎉",
        "bg_gradient_start": "#FFE6EE",
        "bg_gradient_end": "#FFCCE0",
        "border_color": "#F5A0C3",
        "route": "/parties",
        "display_order": 4,
    },
    {
        "name": "Gifts",
        "emoji": "🎁",
        "bg_gradient_start": "#E6F0FF",
        "bg_gradient_end": "#CCE4FF",
        "border_color": "#A0C9F5",
        "route": "/gifts",
        "display_order": 5,
    },
    {
        "name": "Catering",
        "emoji": "👩‍🍳",
        "bg_gradient_start": "#FFF7E6",
        "bg_gradient_end": "#FFF0CC",
        "border_color": "#F5DBA0",
        "route": "/catering",
        "display_order": 6,
    },
]

for s in sectors:
    AppSector.objects.update_or_create(
        name=s["name"],
        defaults=s
    )

print("AppSectors loaded successfully.")

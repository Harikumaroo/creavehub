import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from restaurants.models import Restaurant
from parties.models import PartyPackage

def seed_parties():
    print("Seeding Party Packages...")

    rest1, _ = Restaurant.objects.get_or_create(
        name="The Grand Feast Caterers",
        defaults={"restaurant_type": "dining", "is_active": True}
    )
    rest2, _ = Restaurant.objects.get_or_create(
        name="Chaat Chowk",
        defaults={"restaurant_type": "delivery", "is_active": True}
    )
    rest3, _ = Restaurant.objects.get_or_create(
        name="Spice Route Catering",
        defaults={"restaurant_type": "dining", "is_active": True}
    )

    packages_data = [
        {
            "restaurant": rest1,
            "name": "Silver Jubilee Package",
            "description": "A grand multi-cuisine buffet for 50+ guests. Includes starters, mains, and a wide variety of desserts.",
            "min_guests": 50,
            "max_guests": 200,
            "price_per_person": 1200.00,
            "is_veg": False,
        },
        {
            "restaurant": rest2,
            "name": "Kids Party Special",
            "description": "A wonderful kids party special package from Chaat Chowk. Includes starters, mains, desserts and beverages.",
            "min_guests": 20,
            "max_guests": 200,
            "price_per_person": 350.00,
            "is_veg": True,
        },
        {
            "restaurant": rest3,
            "name": "Corporate Get-Together",
            "description": "An elegant evening package with a curated menu of premium dishes and dedicated service staff.",
            "min_guests": 30,
            "max_guests": 150,
            "price_per_person": 850.00,
            "is_veg": False,
        },
        {
            "restaurant": rest1,
            "name": "Premium Birthday Bash",
            "description": "Celebrate your special day with our signature dishes and a complimentary mocktail counter.",
            "min_guests": 25,
            "max_guests": 100,
            "price_per_person": 950.00,
            "is_veg": False,
        },
    ]

    for data in packages_data:
        package, created = PartyPackage.objects.get_or_create(
            restaurant=data["restaurant"],
            name=data["name"],
            defaults={
                "description": data["description"],
                "min_guests": data["min_guests"],
                "max_guests": data["max_guests"],
                "price_per_person": Decimal(str(data["price_per_person"])),
                "is_veg": data["is_veg"],
                "is_active": True,
                "is_in_stock": True,
            }
        )
        if created:
            print(f"Created: {package.name}")

if __name__ == "__main__":
    seed_parties()
    print("Done!")

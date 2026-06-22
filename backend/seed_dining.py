import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from restaurants.models import Restaurant, RestaurantAddress, RestaurantCategory
from categories.models import Category
from dining.models import DiningVenue
from menu.models import MenuItem

def seed_dining():
    print("Seeding Dining Restaurants...")

    categories_to_seed = [
        "Cafes",
        "Nightlife & Drinks",
        "Family Friendly",
        "Events & Experiences",
        "Rooftop Places",
        "Buffets",
        "Pure Veg",
        "Five-Star Dining"
    ]

    restaurants_data = [
        {
            "name": "The Brew Cafe",
            "cat": "Cafes",
            "image": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&q=80",
            "cost": 600,
            "rating": 4.5,
            "menus": ["Classic Cappuccino", "Avocado Toast", "Blueberry Muffin"]
        },
        {
            "name": "Midnight Lounge",
            "cat": "Nightlife & Drinks",
            "image": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=800&q=80",
            "cost": 2500,
            "rating": 4.8,
            "menus": ["Signature Cocktail", "Nachos Supreme", "Truffle Fries"]
        },
        {
            "name": "Happy Times Diner",
            "cat": "Family Friendly",
            "image": "https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=800&q=80",
            "cost": 800,
            "rating": 4.2,
            "menus": ["Kids Mac & Cheese", "Family Pizza", "Chocolate Sundae"]
        },
        {
            "name": "The Illusionist Show",
            "cat": "Events & Experiences",
            "image": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=800&q=80",
            "cost": 3000,
            "rating": 4.7,
            "menus": ["Mystery Appetizer", "Chef's Special Course", "Liquid Nitrogen Dessert"]
        },
        {
            "name": "Sky High Dine",
            "cat": "Rooftop Places",
            "image": "https://images.unsplash.com/photo-1572116469696-31de0f17cc34?w=800&q=80",
            "cost": 2000,
            "rating": 4.6,
            "menus": ["Grilled Salmon", "Sparkling Wine", "Bruschetta"]
        },
        {
            "name": "Grand Buffet Feast",
            "cat": "Buffets",
            "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80",
            "cost": 1500,
            "rating": 4.3,
            "menus": ["Unlimited Starters", "Continental Main Course", "Dessert Spread"]
        },
        {
            "name": "Green Leaf Pure Veg",
            "cat": "Pure Veg",
            "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80",
            "cost": 500,
            "rating": 4.4,
            "menus": ["Paneer Butter Masala", "Garlic Naan", "Veg Biryani"]
        },
        {
            "name": "The Imperial Dining",
            "cat": "Five-Star Dining",
            "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
            "cost": 5000,
            "rating": 4.9,
            "menus": ["Caviar", "Wagyu Steak", "Gold Leaf Dessert"]
        }
    ]

    for data in restaurants_data:
        # Create Category
        cat_obj, _ = Category.objects.get_or_create(
            name=data["cat"],
            defaults={"is_active": True}
        )

        # Create Restaurant
        rest, created = Restaurant.objects.get_or_create(
            name=data["name"],
            defaults={
                "restaurant_type": "dining",
                "cover_image": data["image"],
                "logo": data["image"],
                "rating": Decimal(str(data["rating"])),
                "is_active": True,
                "is_open": True,
                "is_pure_veg": data["cat"] == "Pure Veg"
            }
        )

        if created:
            print(f"Created Restaurant: {rest.name}")

            # Create Address
            RestaurantAddress.objects.create(
                restaurant=rest,
                address="123 Dining Street",
                city="Chennai",
                state="Tamil Nadu",
                pincode="600001",
                latitude=Decimal("13.0827"),
                longitude=Decimal("80.2707")
            )

            # Map Category
            RestaurantCategory.objects.get_or_create(
                restaurant=rest,
                category=cat_obj
            )

            # Create Dining Venue
            DiningVenue.objects.create(
                restaurant=rest,
                seating_capacity=100,
                has_ac=True,
                avg_cost_for_two=Decimal(str(data["cost"])),
                is_active=True
            )

            # Create Menus
            for menu_item in data["menus"]:
                MenuItem.objects.create(
                    restaurant=rest,
                    name=menu_item,
                    price=Decimal(str(random.randint(200, 1000))),
                    is_available=True,
                    is_veg=data["cat"] == "Pure Veg"
                )

if __name__ == "__main__":
    seed_dining()
    print("Done!")

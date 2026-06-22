import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from restaurants.models import Restaurant
from catering.models import CateringMenu

def seed_catering():
    print("Seeding Non-Veg Catering Menus...")

    # Ensure we have a couple of restaurants to attach these to
    rest1, _ = Restaurant.objects.get_or_create(
        name="The Grand Feast Caterers",
        defaults={"restaurant_type": "dining", "is_active": True}
    )
    rest2, _ = Restaurant.objects.get_or_create(
        name="Royal Non-Veg Banquets",
        defaults={"restaurant_type": "dining", "is_active": True}
    )
    rest3, _ = Restaurant.objects.get_or_create(
        name="Spice Route Catering",
        defaults={"restaurant_type": "dining", "is_active": True}
    )
    rest4, _ = Restaurant.objects.get_or_create(
        name="Green Leaf Pure Veg Caterers",
        defaults={"restaurant_type": "dining", "is_active": True, "is_pure_veg": True}
    )

    menus_data = [
        {
            "restaurant": rest1,
            "name": "Classic Non-Veg Buffet",
            "description": "Chicken Tikka, Mutton Biryani, Butter Chicken, Naan, Desserts",
            "price": 850.00,
            "cuisine": "North Indian",
            "min_plates": 50,
        },
        {
            "restaurant": rest1,
            "name": "Premium Seafood Spread",
            "description": "Prawn Fry, Fish Curry, Squid Rings, Steamed Rice, Dessert",
            "price": 1200.00,
            "cuisine": "Seafood Special",
            "min_plates": 30,
        },
        {
            "restaurant": rest2,
            "name": "Mughlai Royal Feast",
            "description": "Mutton Korma, Chicken Biryani, Seekh Kebab, Shahi Tukda",
            "price": 950.00,
            "cuisine": "Mughlai",
            "min_plates": 40,
        },
        {
            "restaurant": rest2,
            "name": "Hyderabadi Wedding Menu",
            "description": "Hyderabadi Dum Biryani (Chicken/Mutton), Mirchi ka Salan, Double ka Meetha",
            "price": 1100.00,
            "cuisine": "Hyderabadi",
            "min_plates": 100,
        },
        {
            "restaurant": rest3,
            "name": "Chettinad Special",
            "description": "Chettinad Chicken, Mutton Chukka, Parotta, Rice, Rasam",
            "price": 750.00,
            "cuisine": "South Indian",
            "min_plates": 25,
        },
        {
            "restaurant": rest4,
            "name": "Pure Veg Grand Thali",
            "description": "Paneer Butter Masala, Dal Makhani, Mixed Veg, Naan, Jeera Rice, Gulab Jamun",
            "price": 600.00,
            "cuisine": "North Indian Veg",
            "min_plates": 50,
            "is_veg": True,
        },
        {
            "restaurant": rest4,
            "name": "South Indian Veg Feast",
            "description": "Idli, Vada, Dosa, Sambar, 3 Types of Chutney, Pongal, Kesari",
            "price": 450.00,
            "cuisine": "South Indian Veg",
            "min_plates": 100,
            "is_veg": True,
        },
    ]

    for data in menus_data:
        menu, created = CateringMenu.objects.get_or_create(
            restaurant=data["restaurant"],
            name=data["name"],
            defaults={
                "description": data["description"],
                "price_per_plate": Decimal(str(data["price"])),
                "min_plates": data["min_plates"],
                "cuisine_type": data["cuisine"],
                "is_veg": data.get("is_veg", False),
                "is_active": True,
                "is_in_stock": True,
                "image": "https://images.unsplash.com/photo-1555244162-803834f70033?w=1200&q=80"
            }
        )
        if created:
            print(f"Created: {menu.name}")

if __name__ == "__main__":
    seed_catering()
    print("Done!")

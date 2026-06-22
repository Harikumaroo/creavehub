import os
import sys
import random
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()

from django.db import transaction
from categories.models import Category
from restaurants.models import Restaurant, RestaurantCategory
from menu.models import MenuCategory, MenuItem

RESTAURANT_NAMES = [
    "CraveHub Kitchen", "Spice Route", "Burger Hub", "Pizza Paradise", 
    "Healthy Bowl", "Sweet Tooth", "The Asian Wok", "Biryani Central", 
    "South Indian Express", "Cafe Delight", "Grill Master", "Seafood Bay",
    "Taco Town", "Pasta House", "Salad Bar", "Midnight Munchies", 
    "The Breakfast Club", "Dessert Dash", "Vegan Vibes", "Sushi Station"
]

PREFIXES = [
    "Classic", "Spicy", "Special", "Premium", "Homestyle", 
    "Chef's Special", "Ultimate", "Signature", "Double", "Deluxe",
    "Crunchy", "Zesty", "Royal", "Fiery", "Authentic"
]

def run():
    print("Fetching categories...")
    categories = list(Category.objects.all())
    if not categories:
        print("No categories found. Please run load_categories.py first.")
        return

    print("Creating restaurants...")
    restaurants = []
    with transaction.atomic():
        for name in RESTAURANT_NAMES:
            rest, _ = Restaurant.objects.get_or_create(
                name=name,
                defaults={
                    "rating": round(random.uniform(3.5, 4.9), 1),
                    "total_reviews": random.randint(10, 500),
                    "average_delivery_time": random.randint(20, 45),
                    "is_active": True,
                    "cover_image": f"https://source.unsplash.com/800x600/?food,{name.split()[0].lower()}"
                }
            )
            restaurants.append(rest)
            
    print(f"Created/Found {len(restaurants)} restaurants.")

    print("Generating menu items for all categories...")
    items_created = 0

    with transaction.atomic():
        # Removed clean up to preserve existing orders
        pass

        for cat in categories:
            # Pick a random restaurant for this category
            rest = random.choice(restaurants)

            # Link category to restaurant
            RestaurantCategory.objects.get_or_create(
                restaurant=rest,
                category=cat
            )

            # Create MenuCategory
            menu_cat, _ = MenuCategory.objects.get_or_create(
                restaurant=rest,
                name=cat.name,
                defaults={"display_order": random.randint(1, 20)}
            )

            # Generate 5 menu items per category
            for i in range(5):
                prefix = random.choice(PREFIXES)
                item_name = f"{prefix} {cat.name}"
                
                # Make ~20% of items 99 or under
                if random.random() < 0.2:
                    price = random.randint(49, 99)
                    discounted = price
                else:
                    price = random.randint(100, 500)
                    discounted = price - random.randint(10, 50) if random.random() < 0.3 else None

                # Calories: healthy items (<= 450 calories) for EatRight
                is_healthy_cat = any(word in cat.name.lower() for word in ["healthy", "salad", "diet", "vegan", "protein", "fruit"])
                if is_healthy_cat or random.random() < 0.2:
                    calories = random.randint(150, 450)
                else:
                    calories = random.randint(451, 1200)

                # Veg/Non-Veg
                is_veg = True
                if any(word in cat.name.lower() for word in ["chicken", "mutton", "beef", "pork", "fish", "prawn", "seafood", "meat", "egg"]):
                    is_veg = False
                elif random.random() < 0.3: # Randomly some items are non-veg
                    is_veg = False

                MenuItem.objects.create(
                    restaurant=rest,
                    category=menu_cat,
                    name=item_name,
                    description=f"A delicious and {prefix.lower()} preparation of {cat.name}.",
                    price=price,
                    discounted_price=discounted,
                    is_veg=is_veg,
                    is_available=True,
                    calories=calories
                )
                items_created += 1

    print(f"Done! Successfully created {items_created} menu items across {len(restaurants)} restaurants.")

if __name__ == "__main__":
    run()

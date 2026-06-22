import os
import django
import random
from datetime import time as dt_time
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from restaurants.models import Restaurant, RestaurantAddress, RestaurantCategory
from categories.models import Category
from menu.models import MenuItem, MenuCategory

def main():
    # Define the categories
    category_names = [
        ("Snacks", "🍿"),
        ("Ice Creams", "🍦"),
        ("Juices", "🥤"),
        ("Fast Food", "🍔")
    ]
    
    categories = []
    for name, emoji in category_names:
        cat, created = Category.objects.get_or_create(
            name=name,
            defaults={'emoji': emoji}
        )
        categories.append(cat)
        
    adjectives = ["Midnight", "Night Owl", "Moonlight", "Late Night", "Dark", "Starry", "Nighthawk", "Shadow", "Sleepless", "Dream", "Twilight", "Lunar"]
    nouns = ["Bites", "Cravings", "Snacks", "Treats", "Eats", "Diner", "Cafe", "Stop", "Hub", "Junction", "Spot", "Station", "Lounge", "Grill", "Bistro"]
    
    cities = ["Mumbai", "Delhi", "Bangalore", "Pune", "Hyderabad"]

    print("Generating 50 midnight restaurants...")
    
    restaurants_created = 0
    
    for i in range(50):
        name = f"{random.choice(adjectives)} {random.choice(nouns)} {i+1}"
        cat = random.choice(categories)
        city = random.choice(cities)
        
        # Decide if it's dining or food delivery
        rest_type = Restaurant.RestaurantType.DINING if random.random() < 0.4 else Restaurant.RestaurantType.FOOD
        
        restaurant = Restaurant.objects.create(
            name=name,
            description=f"Best {cat.name} available late at night!",
            rating=Decimal(str(round(random.uniform(3.5, 5.0), 1))),
            total_reviews=random.randint(10, 500),
            average_delivery_time=random.randint(20, 60),
            minimum_order_amount=Decimal(str(random.choice([0, 99, 149]))),
            delivery_fee=Decimal(str(random.choice([0, 20, 40]))),
            is_pure_veg=random.random() < 0.3,
            is_active=True,
            is_open=True,
            is_featured=random.random() < 0.2,
            restaurant_type=rest_type,
            opening_time=dt_time(0, 0),  # 12 AM
            closing_time=dt_time(4, 0),  # 4 AM
            is_24hrs=False
        )
        
        RestaurantAddress.objects.create(
            restaurant=restaurant,
            address=f"{random.randint(1, 999)}, Night Market Street",
            city=city,
            state="State",
            country="India",
            pincode=f"40000{random.randint(1, 9)}",
            latitude=Decimal(str(round(random.uniform(18.9, 19.2), 6))),
            longitude=Decimal(str(round(random.uniform(72.8, 73.0), 6)))
        )
        
        RestaurantCategory.objects.create(
            restaurant=restaurant,
            category=cat
        )
        
        
        # Create a MenuCategory for the restaurant
        menu_cat, _ = MenuCategory.objects.get_or_create(
            restaurant=restaurant,
            name=cat.name
        )
        
        # Add 3 dummy menu items per restaurant
        for j in range(3):
            MenuItem.objects.create(
                restaurant=restaurant,
                category=menu_cat,
                name=f"{cat.name} Special {j+1}",
                description=f"Delicious {cat.name.lower()} to satisfy your midnight cravings.",
                price=Decimal(str(random.randint(50, 300))),
                is_veg=restaurant.is_pure_veg or random.random() < 0.7,
                is_available=True
            )
            
        restaurants_created += 1

    print(f"Successfully created {restaurants_created} midnight restaurants!")

if __name__ == '__main__':
    main()

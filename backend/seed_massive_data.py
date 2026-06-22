import os
import sys
import django
import random
from decimal import Decimal

sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from categories.models import Category
from restaurants.models import Restaurant, RestaurantCategory, RestaurantAddress
from menu.models import MenuCategory, MenuItem

RAW_DATA = """
🍛 Indian Restaurants
South Indian
North Indian
Andhra
Chettinad
Kerala
Tamil Nadu Traditional
Hyderabadi
Mughlai
Punjabi
Bengali
Gujarati
Maharashtrian
Rajasthani
Kashmiri
Goan
Odia
Assamese

🍚 Biryani Restaurants
Hyderabadi Biryani
Ambur Biryani
Dindigul Biryani
Thalassery Biryani
Lucknowi Biryani
Kolkata Biryani
Donne Biryani

🍔 Fast Food Restaurants
Burgers
Fries
Sandwiches
Wraps
Hot Dogs
Nuggets

🍕 Pizza Restaurants
Italian Pizza
Wood Fired Pizza
Deep Dish Pizza
Gourmet Pizza

🍜 Asian Restaurants
Chinese
Thai
Japanese
Korean
Vietnamese
Indonesian
Malaysian

🍣 Japanese Restaurants
Sushi
Ramen
Bento
Tempura

🌮 Mexican Restaurants
Tacos
Burritos
Quesadillas
Nachos

🍝 Italian Restaurants
Pasta
Lasagna
Risotto
Garlic Bread
Ravioli

🥗 Healthy Food Restaurants
Salads
Protein Meals
Keto Meals
Low-Calorie Meals
Gluten-Free Meals
High Protein Meals
No Added Sugar Meals

🥙 Arabian & Middle Eastern
Shawarma
Mandi
Kebabs
Falafel
Hummus
Grills

🍗 BBQ & Grill Restaurants
Barbecue
Tandoori
Grilled Chicken
Smoked Meat

🥘 Seafood Restaurants
Fish Fry
Prawns
Crab
Lobster
Coastal Cuisine

☕ Cafe & Bakery
Coffee Shops
Tea Cafes
Dessert Cafes
Bakeries
Artisan Breads

🍰 Desserts & Ice Cream
Cakes
Pastries
Ice Cream
Waffles
Donuts
Brownies

🧃 Beverage Stores
Juices
Smoothies
Milkshakes
Bubble Tea
Mocktails

🥬 Pure Veg Restaurants
Jain Food
Vegetarian Meals
Veg Thali
Temple Style Food

🍖 Non-Veg Speciality Restaurants
Chicken Special
Mutton Special
Seafood Special
Grill Special

🌙 Late Night Restaurants
Midnight Biryani
Late Night Snacks
24x7 Restaurants

☁️ Cloud Kitchens
Delivery-only Brands
Multi-brand Kitchens
Virtual Restaurants
"""

def generate_menu_items(restaurant, name):
    menu_cat, _ = MenuCategory.objects.get_or_create(
        restaurant=restaurant,
        name="Recommended",
        defaults={"display_order": 1}
    )

    items = [
        f"Classic {name} Special",
        f"Spicy {name} Delight",
        f"Premium {name} Platter"
    ]

    for item_name in items:
        price = random.randint(150, 600)
        MenuItem.objects.get_or_create(
            restaurant=restaurant,
            name=item_name,
            defaults={
                "category": menu_cat,
                "description": f"A wonderful {item_name.lower()} prepared with fresh ingredients.",
                "price": Decimal(str(price)),
                "is_veg": random.choice([True, False]),
                "is_available": True,
                "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&q=80"
            }
        )

def seed():
    print("Starting massive database seed...")
    lines = RAW_DATA.strip().split('\n')
    
    current_category = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # If line contains an emoji, it's a main category
        if any(char for char in line if ord(char) > 10000):
            emoji = line.split(' ')[0]
            cat_name = ' '.join(line.split(' ')[1:])
            current_category, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    "emoji": emoji,
                    "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=80",
                    "is_active": True
                }
            )
            print(f"Created Category: {cat_name}")
        else:
            # It's a subcategory/restaurant
            if not current_category:
                continue
                
            rest_name = f"The {line} House"
            is_veg = "Veg" in line or "Jain" in line or current_category.name == "Pure Veg Restaurants"
            
            rest, created = Restaurant.objects.get_or_create(
                name=rest_name,
                defaults={
                    "description": f"Authentic {line} cuisine. Best in the city!",
                    "rating": Decimal(str(round(random.uniform(3.5, 4.9), 1))),
                    "total_reviews": random.randint(50, 1000),
                    "is_pure_veg": is_veg,
                    "is_active": True,
                    "restaurant_type": "food",
                    "cover_image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80"
                }
            )
            
            if created:
                # Add to category
                RestaurantCategory.objects.get_or_create(
                    restaurant=rest,
                    category=current_category
                )
                
                # Add Address
                RestaurantAddress.objects.get_or_create(
                    restaurant=rest,
                    defaults={
                        "address": f"123 {line} Street",
                        "city": "Metropolis",
                        "state": "State",
                        "pincode": "100001",
                        "latitude": Decimal("12.9716"),
                        "longitude": Decimal("77.5946")
                    }
                )
                
                # Generate Menu Items
                generate_menu_items(rest, line)
                print(f"  Created Restaurant & Menu: {rest_name}")

if __name__ == "__main__":
    seed()
    print("Done seeding massive data!")

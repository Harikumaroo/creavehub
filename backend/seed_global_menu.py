import os
import sys
import django
import random
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from restaurants.models import Restaurant
from menu.models import MenuCategory, MenuItem

# Massive global food list
GLOBAL_FOODS = {
    "Beverages": [
        {"name": "Hot Coffee", "price": 49.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1551030173-122aabc4489c?w=500&h=500&fit=crop"},
        {"name": "Cappuccino", "price": 99.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1534040385115-33dcb3acba5b?w=500&h=500&fit=crop"},
        {"name": "Espresso", "price": 79.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=500&h=500&fit=crop"},
        {"name": "Iced Latte", "price": 129.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=500&h=500&fit=crop"},
        {"name": "Chocolate Milkshake", "price": 149.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&h=500&fit=crop"},
        {"name": "Masala Chai", "price": 39.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1561336313-0bd5e0b27ec8?w=500&h=500&fit=crop"},
    ],
    "Indian Classics": [
        {"name": "Hot Chicken Biryani", "price": 249.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&h=500&fit=crop"},
        {"name": "Mutton Biryani", "price": 349.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1631515243349-e0cb75fb8d3a?w=500&h=500&fit=crop"},
        {"name": "Butter Chicken", "price": 299.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=500&h=500&fit=crop"},
        {"name": "Paneer Tikka Masala", "price": 249.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&h=500&fit=crop"},
        {"name": "Masala Dosa", "price": 99.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1589301760014-d929f39ce9b1?w=500&h=500&fit=crop"},
        {"name": "Chole Bhature", "price": 129.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1626082895617-2c676999cb84?w=500&h=500&fit=crop"},
        {"name": "Samosa", "price": 29.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500&h=500&fit=crop"},
        {"name": "Garlic Naan", "price": 49.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1601050690117-94f5f6af26f8?w=500&h=500&fit=crop"},
    ],
    "Italian": [
        {"name": "Margherita Pizza", "price": 199.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&h=500&fit=crop"},
        {"name": "Pepperoni Pizza", "price": 299.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=500&h=500&fit=crop"},
        {"name": "Pasta Carbonara", "price": 249.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=500&h=500&fit=crop"},
        {"name": "Lasagna", "price": 279.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=500&h=500&fit=crop"},
    ],
    "American & Fast Food": [
        {"name": "Classic Cheeseburger", "price": 149.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&h=500&fit=crop"},
        {"name": "French Fries", "price": 89.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1576107232684-1279f390859f?w=500&h=500&fit=crop"},
        {"name": "Hot Dog", "price": 99.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1612392166886-ee8475b03af2?w=500&h=500&fit=crop"},
        {"name": "Spicy Chicken Wings", "price": 199.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1569691899455-88464f6d3ab1?w=500&h=500&fit=crop"},
    ],
    "Asian": [
        {"name": "Spicy Ramen", "price": 249.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=500&h=500&fit=crop"},
        {"name": "Sushi Roll", "price": 349.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=500&h=500&fit=crop"},
        {"name": "Dim Sum", "price": 199.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=500&h=500&fit=crop"},
        {"name": "Chicken Fried Rice", "price": 179.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&h=500&fit=crop"},
        {"name": "Spring Rolls", "price": 129.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1544025162-d76694265947?w=500&h=500&fit=crop"},
    ],
    "Mexican": [
        {"name": "Beef Tacos", "price": 159.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=500&h=500&fit=crop"},
        {"name": "Chicken Burrito", "price": 199.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=500&h=500&fit=crop"},
        {"name": "Cheesy Nachos", "price": 149.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?w=500&h=500&fit=crop"},
    ],
    "Middle Eastern": [
        {"name": "Chicken Shawarma", "price": 129.00, "is_veg": False, "image": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=500&h=500&fit=crop"},
        {"name": "Falafel Wrap", "price": 119.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1593504049359-715339e163be?w=500&h=500&fit=crop"},
    ],
    "Desserts": [
        {"name": "Chocolate Brownie", "price": 129.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&h=500&fit=crop"},
        {"name": "New York Cheesecake", "price": 179.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500&h=500&fit=crop"},
        {"name": "Ice Cream Sundae", "price": 149.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1563805042-7684c8a9e9ce?w=500&h=500&fit=crop"},
        {"name": "Gulab Jamun", "price": 79.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1605197136006-2580a6b7d41a?w=500&h=500&fit=crop"},
        {"name": "Belgian Waffles", "price": 159.00, "is_veg": True, "image": "https://images.unsplash.com/photo-1562376552-0d160a2f5fbc?w=500&h=500&fit=crop"},
    ]
}

def run():
    restaurants = list(Restaurant.objects.all())
    if not restaurants:
        print("No restaurants found. Create some restaurants first.")
        return

    items_added = 0
    
    # We will just add ALL categories to the first restaurant for simplicity,
    # or distribute them across available restaurants.
    
    for category_name, foods in GLOBAL_FOODS.items():
        # Pick a random restaurant or just the first one to ensure it has everything
        for rest in restaurants:
            # Create or get category
            cat, _ = MenuCategory.objects.get_or_create(
                restaurant=rest, 
                name=category_name,
                defaults={"display_order": 1}
            )
            
            for food in foods:
                # Add item if it doesn't exist
                item, created = MenuItem.objects.get_or_create(
                    restaurant=rest,
                    name=food["name"],
                    defaults={
                        "category": cat,
                        "price": Decimal(str(food["price"])),
                        "is_veg": food["is_veg"],
                        "image": food["image"],
                        "description": f"Delicious {food['name']} prepared with the best ingredients."
                    }
                )
                if created:
                    items_added += 1

    print(f"Successfully seeded {items_added} new global food items!")

if __name__ == "__main__":
    run()

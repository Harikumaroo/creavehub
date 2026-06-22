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

# Mapping of categories to a realistic restaurant name and list of realistic dishes
DATA = {
    "Pizza": {
        "restaurant": "The Artisan Pizza Co.",
        "dishes": [
            ("Margherita Pizza", "Classic delight with 100% real mozzarella cheese", 299, True),
            ("Pepperoni Pizza", "Loaded with pepperoni and extra cheese", 450, False),
            ("Farmhouse Pizza", "Onion, crisp capsicum, mushroom & fresh tomato", 399, True)
        ]
    },
    "Burgers": {
        "restaurant": "Burger King's Street",
        "dishes": [
            ("Classic Veg Burger", "Crispy veg patty with fresh veggies and mayo", 149, True),
            ("Chicken Zinger Burger", "Signature crispy chicken fillet with lettuce", 199, False),
            ("Double Cheese Burger", "Two juicy patties layered with double cheese", 249, False)
        ]
    },
    "South Indian": {
        "restaurant": "Dakshin Delights",
        "dishes": [
            ("Masala Dosa", "Crispy crepe served with sambar and coconut chutney", 120, True),
            ("Idli Vada Combo", "Steamed rice cakes with crispy lentil donuts", 90, True),
            ("Chicken Chettinad", "Spicy and aromatic chicken curry from Tamil Nadu", 280, False)
        ]
    },
    "Chinese": {
        "restaurant": "Dragon Wok",
        "dishes": [
            ("Hakka Noodles", "Wok tossed noodles with fresh vegetables", 180, True),
            ("Chilli Chicken", "Crispy chicken chunks tossed in spicy sauce", 220, False),
            ("Veg Fried Rice", "Classic fried rice tossed with carrots and beans", 160, True)
        ]
    },
    "Desserts": {
        "restaurant": "Sweet Tooth Confections",
        "dishes": [
            ("Chocolate Lava Cake", "Warm chocolate cake with a gooey molten center", 150, True),
            ("Red Velvet Pastry", "Rich red velvet cake with cream cheese frosting", 120, True),
            ("Gulab Jamun", "Soft and delicious berry sized balls made of milk solids", 80, True)
        ]
    },
    "Healthy": {
        "restaurant": "Green Bowl Eats",
        "dishes": [
            ("Grilled Chicken Salad", "Fresh greens tossed with grilled chicken breast", 250, False),
            ("Quinoa Bowl", "Nutritious bowl with quinoa, avocado and veggies", 220, True),
            ("Detox Green Juice", "Freshly cold-pressed spinach, celery, and apple", 180, True)
        ]
    },
    "Beverages": {
        "restaurant": "The Sip Station",
        "dishes": [
            ("Cold Coffee", "Thick and creamy cold coffee with chocolate syrup", 140, True),
            ("Mango Smoothie", "Fresh tropical mango blended with yogurt", 160, True),
            ("Virgin Mojito", "Refreshing mocktail with mint and lime", 120, True)
        ]
    },
    "North Indian": {
        "restaurant": "Punjab Grill",
        "dishes": [
            ("Butter Chicken", "Tender chicken cooked in rich tomato gravy", 350, False),
            ("Paneer Tikka Masala", "Grilled paneer cubes in spicy onion tomato gravy", 280, True),
            ("Garlic Naan", "Soft Indian bread flavored with garlic and butter", 60, True)
        ]
    },
    "Rolls": {
        "restaurant": "Kolkata Roll Center",
        "dishes": [
            ("Chicken Egg Roll", "Spicy chicken wrapped in a flaky egg paratha", 150, False),
            ("Paneer Kathi Roll", "Grilled paneer with onions and mint chutney", 130, True),
            ("Double Egg Roll", "Classic street-style double egg roll", 90, False)
        ]
    },
    "Ice Cream": {
        "restaurant": "Frosty Scoops",
        "dishes": [
            ("Belgian Chocolate Scoop", "Rich and dark chocolate premium ice cream", 110, True),
            ("Vanilla Sundae", "Classic vanilla topped with nuts and syrup", 140, True),
            ("Mango Sorbet", "Dairy-free refreshing mango sorbet", 130, True)
        ]
    },
    "Street Food": {
        "restaurant": "Chaat Bazaar",
        "dishes": [
            ("Pani Puri", "Crispy puris filled with spicy tangy water", 60, True),
            ("Pav Bhaji", "Spicy vegetable mash served with buttered bread", 120, True),
            ("Aloo Tikki Chaat", "Crispy potato patties topped with chutneys", 80, True)
        ]
    },
    "Bakery": {
        "restaurant": "The Daily Bread",
        "dishes": [
            ("Butter Croissant", "Flaky and buttery French pastry", 90, True),
            ("Blueberry Muffin", "Soft muffin bursting with fresh blueberries", 110, True),
            ("Multigrain Loaf", "Freshly baked healthy multigrain bread", 80, True)
        ]
    },
    "Kebab": {
        "restaurant": "Sultan's Kebab House",
        "dishes": [
            ("Mutton Seekh Kebab", "Minced mutton blended with aromatic spices", 320, False),
            ("Chicken Tikka", "Juicy boneless chicken marinated in yogurt and spices", 280, False),
            ("Hara Bhara Kebab", "Vegetarian kebab made with spinach and peas", 200, True)
        ]
    },
    "Momos": {
        "restaurant": "Himalayan Momos",
        "dishes": [
            ("Steamed Chicken Momos", "Authentic Tibetan dumplings filled with chicken", 140, False),
            ("Fried Veg Momos", "Crispy fried dumplings with vegetable filling", 120, True),
            ("Paneer Kurkure Momos", "Crunchy coated momos stuffed with paneer", 160, True)
        ]
    },
    "Noodles": {
        "restaurant": "Noodle Factory",
        "dishes": [
            ("Schezwan Noodles", "Spicy noodles tossed in fiery Schezwan sauce", 180, True),
            ("Chicken Garlic Noodles", "Wok tossed noodles with burnt garlic and chicken", 210, False),
            ("Pad Thai", "Classic Thai style flat rice noodles with peanuts", 240, True)
        ]
    }
}

def seed():
    print("Seeding specific dishes for popular categories...")
    
    for cat_name, details in DATA.items():
        rest_name = details["restaurant"]
        dishes = details["dishes"]
        
        # 1. Create or get category
        category, _ = Category.objects.get_or_create(
            name=cat_name,
            defaults={
                "is_active": True,
                "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=80"
            }
        )
        print(f"Ensured Category: {cat_name}")
        
        # 2. Create or get restaurant
        rest, created = Restaurant.objects.get_or_create(
            name=rest_name,
            defaults={
                "description": f"The best place for {cat_name} in town.",
                "rating": Decimal(str(round(random.uniform(4.0, 4.9), 1))),
                "total_reviews": random.randint(100, 2000),
                "is_pure_veg": all(d[3] for d in dishes),
                "is_active": True,
                "restaurant_type": "food",
                "cover_image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80"
            }
        )
        
        RestaurantCategory.objects.get_or_create(
            restaurant=rest,
            category=category
        )
        
        if created:
            RestaurantAddress.objects.get_or_create(
                restaurant=rest,
                defaults={
                    "address": f"Center Square, {cat_name} Lane",
                    "city": "Metropolis",
                    "state": "State",
                    "pincode": "100001",
                    "latitude": Decimal("12.9716"),
                    "longitude": Decimal("77.5946")
                }
            )
        
        # 3. Add Dishes
        menu_cat, _ = MenuCategory.objects.get_or_create(
            restaurant=rest,
            name="Recommended",
            defaults={"display_order": 1}
        )
        
        for name, desc, price, is_veg in dishes:
            item, i_created = MenuItem.objects.get_or_create(
                restaurant=rest,
                name=name,
                defaults={
                    "category": menu_cat,
                    "description": desc,
                    "price": Decimal(str(price)),
                    "is_veg": is_veg,
                    "is_available": True,
                    "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&q=80"
                }
            )
            if i_created:
                print(f"  Added Dish: {name} (₹{price})")

if __name__ == "__main__":
    seed()
    print("Done adding sample dishes!")

import random
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from restaurants.models import Restaurant
from menu.models import MenuCategory, MenuItem

# Configuration
TOTAL_RESTAURANTS = 150
ITEMS_PER_RESTAURANT_TARGET = 175  # ~26,250 items total across 150 restaurants

RESTAURANT_TYPES = [
    "SOUTH_INDIAN", "NORTH_INDIAN", "ANDHRA", "CHETTINAD", "KERALA", "HYDERABADI", 
    "MUGHLAI", "PUNJABI", "BENGALI", "GUJARATI", "MAHARASHTRIAN", "RAJASTHANI", 
    "GOAN", "ASSAMESE", "ODIA", "BIRYANI", "PIZZA", "BURGER", "FAST_FOOD", 
    "CHINESE", "THAI", "JAPANESE", "KOREAN", "VIETNAMESE", "MALAYSIAN", 
    "INDONESIAN", "PAN_ASIAN", "MEXICAN", "ITALIAN", "CONTINENTAL", "ARABIAN", 
    "SHAWARMA", "MANDI", "LEBANESE", "TURKISH", "PERSIAN", "BBQ", "GRILL", 
    "KEBAB", "SEAFOOD", "HEALTHY", "KETO", "VEGAN", "ORGANIC", "PURE_VEG", 
    "JAIN", "CAFE", "COFFEE", "BAKERY", "DESSERTS", "ICE_CREAM", "JUICES", 
    "SMOOTHIES", "BUBBLE_TEA", "MILKSHAKES", "CHAAT", "STREET_FOOD", "ROLLS", 
    "MOMOS", "FRIED_CHICKEN", "CLOUD_KITCHEN", "LATE_NIGHT", "CAKE_SHOP", 
    "SWEETS", "CHOCOLATES"
]

# Mapping types to broad themes for realistic generation
THEME_MAPPING = {
    "INDIAN": ["SOUTH_INDIAN", "NORTH_INDIAN", "ANDHRA", "CHETTINAD", "KERALA", "HYDERABADI", "MUGHLAI", "PUNJABI", "BENGALI", "GUJARATI", "MAHARASHTRIAN", "RAJASTHANI", "GOAN", "ASSAMESE", "ODIA", "PURE_VEG", "JAIN"],
    "BIRYANI": ["BIRYANI", "MANDI"],
    "ASIAN": ["CHINESE", "THAI", "JAPANESE", "KOREAN", "VIETNAMESE", "MALAYSIAN", "INDONESIAN", "PAN_ASIAN", "MOMOS"],
    "WESTERN": ["PIZZA", "BURGER", "FAST_FOOD", "MEXICAN", "ITALIAN", "CONTINENTAL", "FRIED_CHICKEN"],
    "MIDDLE_EASTERN": ["ARABIAN", "SHAWARMA", "LEBANESE", "TURKISH", "PERSIAN", "BBQ", "GRILL", "KEBAB"],
    "HEALTHY": ["HEALTHY", "KETO", "VEGAN", "ORGANIC", "SEAFOOD"],
    "CAFE_DESSERTS": ["CAFE", "COFFEE", "BAKERY", "DESSERTS", "ICE_CREAM", "JUICES", "SMOOTHIES", "BUBBLE_TEA", "MILKSHAKES", "CAKE_SHOP", "SWEETS", "CHOCOLATES"],
    "STREET": ["CHAAT", "STREET_FOOD", "ROLLS", "LATE_NIGHT", "CLOUD_KITCHEN"]
}

# Real data dictionaries for procedural generation
RESTAURANT_NAMES_PREFIX = ["The", "Grand", "Royal", "Urban", "Street", "Mama's", "Golden", "Spicy", "Authentic", "Gourmet", "Classic", "Premium", "Daily", "Midnight"]
RESTAURANT_NAMES_SUFFIX = ["Kitchen", "House", "Diner", "Express", "Bistro", "Cafe", "Eats", "Bazaar", "Hub", "Delight", "Point", "Junction", "Palace"]

MENU_CATEGORIES = {
    "INDIAN": ["Best Sellers", "Starters", "Main Course (Veg)", "Main Course (Non-Veg)", "Breads", "Rice Variations", "Accompaniments", "Desserts", "Beverages", "Chef's Specials"],
    "BIRYANI": ["Best Sellers", "Chicken Biryani", "Mutton Biryani", "Veg & Paneer Biryani", "Family Packs", "Starters", "Kebabs", "Desserts", "Beverages", "Combos"],
    "ASIAN": ["Best Sellers", "Soups & Salads", "Dim Sum & Momos", "Appetizers", "Noodles", "Fried Rice", "Main Course (Gravy)", "Sushi & Rolls", "Desserts", "Beverages"],
    "WESTERN": ["Best Sellers", "Pizzas", "Burgers & Sandwiches", "Pasta & Risotto", "Fried Chicken", "Sides & Fries", "Dips", "Desserts", "Beverages", "Meal Deals"],
    "MIDDLE_EASTERN": ["Best Sellers", "Shawarma & Wraps", "Grilled Kebabs", "Mandi & Rice", "Mezze Platters", "Breads", "Desserts", "Beverages", "Chef Specials"],
    "HEALTHY": ["Best Sellers", "Salads", "Keto Bowls", "Protein Meals", "Vegan Specials", "Gluten-Free Sides", "Smoothies", "Cold Pressed Juices", "Guilt-Free Desserts"],
    "CAFE_DESSERTS": ["Best Sellers", "Cakes & Pastries", "Ice Creams & Sundaes", "Waffles & Crepes", "Hot Coffee", "Cold Brews", "Milkshakes & Frappes", "Savory Bites", "Cookies & Breads"],
    "STREET": ["Best Sellers", "Chaat Specials", "Kathi Rolls", "Parathas", "Street Snacks", "Midnight Cravings", "Beverages", "Desserts", "Quick Bites"]
}

FOOD_DICTIONARY = {
    "INDIAN": {
        "veg": [("Paneer Butter Masala", 280, 500), ("Dal Makhani", 220, 350), ("Masala Dosa", 120, 200), ("Palak Paneer", 260, 450), ("Chole Bhature", 180, 600), ("Aloo Gobi", 160, 250), ("Veg Korma", 240, 300), ("Kadai Paneer", 270, 480)],
        "non_veg": [("Butter Chicken", 350, 650), ("Chicken Tikka Masala", 320, 600), ("Mutton Rogan Josh", 450, 550), ("Fish Curry", 380, 400), ("Chicken Chettinad", 330, 500), ("Andhra Chilli Chicken", 290, 450)]
    },
    "BIRYANI": {
        "veg": [("Veg Dum Biryani", 220, 500), ("Paneer Biryani", 260, 600), ("Mushroom Biryani", 250, 450)],
        "non_veg": [("Hyderabadi Chicken Dum Biryani", 320, 800), ("Mutton Biryani", 420, 900), ("Chicken Fry Piece Biryani", 340, 850), ("Egg Biryani", 240, 600), ("Prawns Biryani", 450, 750), ("Kolkata Chicken Biryani", 310, 750)]
    },
    "ASIAN": {
        "veg": [("Veg Hakka Noodles", 180, 350), ("Veg Manchurian", 200, 300), ("Chilli Paneer", 240, 400), ("Veg Fried Rice", 170, 350), ("Mushroom Salt & Pepper", 220, 250)],
        "non_veg": [("Chilli Chicken", 260, 450), ("Chicken Fried Rice", 220, 400), ("Chicken Hakka Noodles", 230, 400), ("Kung Pao Chicken", 310, 500), ("Prawn Tempura", 450, 300), ("Chicken Momos", 160, 250)]
    },
    "WESTERN": {
        "veg": [("Margherita Pizza", 299, 600), ("Veggie Supreme Pizza", 399, 700), ("Classic Veg Burger", 149, 450), ("Cheese Fries", 129, 350), ("Alfredo Pasta", 350, 550), ("Garlic Bread", 119, 250)],
        "non_veg": [("Pepperoni Pizza", 450, 800), ("Chicken Zinger Burger", 199, 550), ("BBQ Chicken Pizza", 420, 750), ("Crispy Fried Chicken (2pcs)", 220, 600), ("Chicken Nuggets", 150, 400)]
    },
    "MIDDLE_EASTERN": {
        "veg": [("Falafel Wrap", 180, 400), ("Hummus with Pita", 220, 300), ("Paneer Shawarma", 200, 450), ("Fattoush Salad", 160, 150)],
        "non_veg": [("Chicken Shawarma", 190, 500), ("Mutton Seekh Kebab", 350, 450), ("Chicken Mandi", 480, 900), ("Grilled Chicken (Half)", 380, 600), ("Chicken Tikka Kebab", 320, 450)]
    },
    "HEALTHY": {
        "veg": [("Quinoa Salad Bowl", 280, 300), ("Tofu Scramble", 240, 250), ("Avocado Toast", 260, 350), ("Green Detox Smoothie", 180, 150), ("Oatmeal Bowl", 200, 250)],
        "non_veg": [("Grilled Chicken Salad", 320, 350), ("Keto Baked Fish", 450, 400), ("Chicken Breast with Veggies", 350, 400), ("Egg White Omelette", 180, 200)]
    },
    "CAFE_DESSERTS": {
        "veg": [("Chocolate Lava Cake", 180, 450), ("Blueberry Cheesecake", 220, 400), ("Cappuccino", 150, 100), ("Cold Coffee", 180, 250), ("Mango Smoothie", 160, 200), ("Red Velvet Cupcake", 120, 300), ("Hazelnut Frappe", 210, 350), ("Brownie Sundae", 250, 550)],
        "non_veg": [] # Generally handled as veg
    },
    "STREET": {
        "veg": [("Pani Puri", 60, 150), ("Pav Bhaji", 120, 350), ("Aloo Tikki Chaat", 80, 200), ("Vada Pav", 50, 250), ("Veg Kathi Roll", 130, 300)],
        "non_veg": [("Chicken Egg Roll", 160, 450), ("Double Egg Roll", 100, 350), ("Chicken Keema Pav", 180, 400)]
    }
}

MODIFIERS = ["Spicy", "Extra Cheese", "Special", "Jumbo", "Mini", "Regular", "Large", "Combo", "Supreme", "Classic", "Premium", "Homestyle", "Fiery", "Tandoori"]

class Command(BaseCommand):
    help = 'Seeds the database with 100+ restaurants and 25,000+ menu items'

    def get_theme(self, rest_type):
        for theme, types in THEME_MAPPING.items():
            if rest_type in types:
                return theme
        return "WESTERN"

    def get_realistic_name(self, rest_type):
        theme = self.get_theme(rest_type)
        prefix = random.choice(RESTAURANT_NAMES_PREFIX)
        suffix = random.choice(RESTAURANT_NAMES_SUFFIX)
        base = rest_type.replace("_", " ").title()
        
        patterns = [
            f"{prefix} {base} {suffix}",
            f"{base} {suffix}",
            f"{prefix} {base}",
            f"The {base} Experience"
        ]
        return random.choice(patterns)

    @transaction.atomic
    def handle(self, *args, **options):
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
        self.stdout.write(self.style.WARNING("Starting mass data deletion..."))
        MenuItem.objects.all().delete()
        MenuCategory.objects.all().delete()
        Restaurant.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Cleared existing data."))

        # 1. CREATE RESTAURANTS
        self.stdout.write(self.style.WARNING(f"Creating {TOTAL_RESTAURANTS} Restaurants..."))
        restaurants = []
        for i in range(TOTAL_RESTAURANTS):
            rest_type = random.choice(RESTAURANT_TYPES)
            name = f"{self.get_realistic_name(rest_type)} {i+1}"
            
            rest = Restaurant(
                id=uuid.uuid4(),
                name=name,
                slug=slugify(f"{name}-{uuid.uuid4().hex[:6]}"),
                description=f"Authentic and premium {rest_type.replace('_', ' ').title()} cuisine.",
                logo="https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=200&q=80",
                cover_image="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&q=80",
                rating=Decimal(str(round(random.uniform(3.5, 4.9), 1))),
                total_reviews=random.randint(50, 5000),
                average_delivery_time=random.randint(20, 60),
                minimum_order_amount=Decimal(str(random.choice([0, 99, 149, 199]))),
                delivery_fee=Decimal(str(random.choice([0, 20, 40, 60]))),
                preparation_time=random.randint(10, 30),
                is_open=random.choice([True, True, True, False]),
                is_featured=random.choice([True, False, False]),
                is_active=True,
                is_pure_veg=rest_type in ["PURE_VEG", "JAIN", "VEGAN", "ORGANIC", "SWEETS", "CHOCOLATES", "JUICES"],
                restaurant_type="food"
            )
            restaurants.append(rest)
            
        Restaurant.objects.bulk_create(restaurants, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {TOTAL_RESTAURANTS} Restaurants."))

        # 2. CREATE MENU CATEGORIES
        self.stdout.write(self.style.WARNING("Creating Categories..."))
        categories = []
        rest_cat_map = {}  # {rest_id: [cat1, cat2, ...]}
        
        for rest in restaurants:
            theme = self.get_theme(next((t for t in RESTAURANT_TYPES if t.lower() in rest.slug), "WESTERN"))
            cat_names = MENU_CATEGORIES.get(theme, MENU_CATEGORIES["WESTERN"])
            
            rest_cats = []
            for order, cat_name in enumerate(cat_names):
                cat = MenuCategory(
                    id=uuid.uuid4(),
                    restaurant_id=rest.id,
                    name=cat_name,
                    display_order=order
                )
                categories.append(cat)
                rest_cats.append(cat)
            rest_cat_map[rest.id] = rest_cats

        MenuCategory.objects.bulk_create(categories, batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(categories)} Categories."))

        # 3. CREATE MENU ITEMS
        self.stdout.write(self.style.WARNING(f"Creating Menu Items (~{TOTAL_RESTAURANTS * ITEMS_PER_RESTAURANT_TARGET} items)..."))
        menu_items = []
        
        for rest in restaurants:
            theme = self.get_theme(next((t for t in RESTAURANT_TYPES if t.lower() in rest.slug), "WESTERN"))
            food_options_veg = FOOD_DICTIONARY.get(theme, FOOD_DICTIONARY["WESTERN"])["veg"]
            food_options_non_veg = FOOD_DICTIONARY.get(theme, FOOD_DICTIONARY["WESTERN"])["non_veg"]
            
            all_options = food_options_veg + (food_options_non_veg if not rest.is_pure_veg else [])
            if not all_options:
                all_options = FOOD_DICTIONARY["WESTERN"]["veg"]
                
            cats = rest_cat_map[rest.id]
            
            # Generate items to hit the target count
            for _ in range(ITEMS_PER_RESTAURANT_TARGET):
                base_food = random.choice(all_options)
                modifier = random.choice(MODIFIERS)
                
                food_name, base_price, base_cal = base_food
                is_veg = base_food in food_options_veg
                
                final_name = f"{modifier} {food_name}"
                price = Decimal(str(base_price + random.randint(10, 100)))
                
                has_discount = random.choice([True, False, False])
                discounted_price = Decimal(str(int(price) - random.randint(10, 50))) if has_discount else None
                
                item = MenuItem(
                    id=uuid.uuid4(),
                    restaurant_id=rest.id,
                    category_id=random.choice(cats).id,
                    name=final_name,
                    description=f"Freshly prepared {final_name.lower()} with premium ingredients. A chef's special.",
                    image="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80",
                    price=price,
                    discounted_price=discounted_price,
                    is_veg=is_veg,
                    is_available=True,
                    is_in_stock=random.choice([True, True, True, True, False]),
                    calories=base_cal + random.randint(0, 200)
                )
                menu_items.append(item)

        # Bulk create in chunks to avoid memory overload
        batch_size = 5000
        for i in range(0, len(menu_items), batch_size):
            MenuItem.objects.bulk_create(menu_items[i:i + batch_size], batch_size=batch_size)
            
        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(menu_items)} Menu Items."))
        self.stdout.write(self.style.SUCCESS("🎉 Seeding Completed Successfully!"))

"""
CraveHub — Load Master Food Categories & Subcategories
Run: python scripts/load_categories.py
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()

from categories.models import Category

CATEGORIES = [
    {
        "name": "Indian Cuisine", "emoji": "🍛", "display_order": 1,
        "subcategories": [
            "South Indian", "North Indian", "Andhra", "Telangana", "Chettinad",
            "Kerala", "Karnataka", "Tamil Nadu Special", "Hyderabadi", "Punjabi",
            "Gujarati", "Bengali", "Maharashtrian", "Rajasthani", "Kashmiri",
            "Goan", "Mughlai", "Awadhi", "Lucknowi", "Street Food",
        ],
    },
    {
        "name": "Biryani & Rice", "emoji": "🍚", "display_order": 2,
        "subcategories": [
            "Chicken Biryani", "Mutton Biryani", "Egg Biryani", "Veg Biryani",
            "Seafood Biryani", "Dum Biryani", "Fried Rice", "Pulao", "Rice Bowls",
        ],
    },
    {
        "name": "Fast Food", "emoji": "🍔", "display_order": 3,
        "subcategories": [
            "Burgers", "Pizza", "Sandwiches", "Wraps", "Hot Dogs",
            "French Fries", "Nuggets", "Subs",
        ],
    },
    {
        "name": "Chinese Cuisine", "emoji": "🥢", "display_order": 4,
        "subcategories": [
            "Indo-Chinese", "Hakka", "Sichuan", "Cantonese",
            "Noodles", "Chinese Fried Rice", "Dim Sum", "Momos",
        ],
    },
    {
        "name": "Asian Cuisine", "emoji": "🌏", "display_order": 5,
        "subcategories": [
            "Japanese", "Korean", "Thai", "Vietnamese",
            "Indonesian", "Malaysian", "Singaporean", "Filipino",
        ],
    },
    {
        "name": "Korean Food", "emoji": "🇰🇷", "display_order": 6,
        "subcategories": [
            "Korean BBQ", "Bibimbap", "Kimchi", "Korean Fried Chicken",
            "Tteokbokki", "Ramyeon",
        ],
    },
    {
        "name": "Japanese Food", "emoji": "🇯🇵", "display_order": 7,
        "subcategories": [
            "Sushi", "Sashimi", "Ramen", "Udon", "Tempura", "Bento", "Donburi",
        ],
    },
    {
        "name": "Thai Food", "emoji": "🇹🇭", "display_order": 8,
        "subcategories": [
            "Thai Curry", "Pad Thai", "Thai Fried Rice", "Thai Soups",
        ],
    },
    {
        "name": "Italian Cuisine", "emoji": "🍝", "display_order": 9,
        "subcategories": [
            "Pasta", "Italian Pizza", "Risotto", "Lasagna", "Ravioli", "Gnocchi",
        ],
    },
    {
        "name": "American Cuisine", "emoji": "🦅", "display_order": 10,
        "subcategories": [
            "American Burgers", "BBQ", "Fried Chicken", "Steaks", "Wings", "American Hot Dogs",
        ],
    },
    {
        "name": "Mexican Cuisine", "emoji": "🌮", "display_order": 11,
        "subcategories": [
            "Tacos", "Burritos", "Nachos", "Quesadillas", "Enchiladas",
        ],
    },
    {
        "name": "Mediterranean Cuisine", "emoji": "🫒", "display_order": 12,
        "subcategories": [
            "Falafel", "Hummus", "Shawarma", "Mediterranean Kebabs", "Pita", "Mezze",
        ],
    },
    {
        "name": "Middle Eastern Cuisine", "emoji": "🕌", "display_order": 13,
        "subcategories": [
            "Middle Eastern Shawarma", "Mandi", "Kabsa", "Middle Eastern Grilled Chicken", "Middle Eastern Kebabs",
        ],
    },
    {
        "name": "Arabian Cuisine", "emoji": "🌙", "display_order": 14,
        "subcategories": [
            "Arabian Mandi", "Arabian Kabsa", "Arabian Shawarma", "Arabian Grills",
        ],
    },
    {
        "name": "Turkish Cuisine", "emoji": "🇹🇷", "display_order": 15,
        "subcategories": [
            "Doner Kebab", "Turkish Pizza", "Baklava",
        ],
    },
    {
        "name": "European Cuisine", "emoji": "🇪🇺", "display_order": 16,
        "subcategories": [
            "French", "German", "Spanish", "Greek", "Portuguese",
        ],
    },
    {
        "name": "Seafood", "emoji": "🦞", "display_order": 17,
        "subcategories": [
            "Fish", "Prawns", "Crab", "Lobster", "Squid", "Mussels",
        ],
    },
    {
        "name": "Grill & BBQ", "emoji": "🔥", "display_order": 18,
        "subcategories": [
            "BBQ Chicken", "Tandoori", "Grilled Kebabs", "Grilled Fish", "Grilled Veggies",
        ],
    },
    {
        "name": "Healthy Food", "emoji": "🥗", "display_order": 19,
        "subcategories": [
            "Salads", "Protein Bowls", "Keto Meals", "Vegan Meals",
            "Diet Meals", "Millet Meals", "Organic Food", "High Protein Meals",
        ],
    },
    {
        "name": "Vegetarian", "emoji": "🌿", "display_order": 20,
        "subcategories": [
            "Pure Veg", "Jain Food", "Vegan Food", "Satvik Food",
        ],
    },
    {
        "name": "Breakfast", "emoji": "🌅", "display_order": 21,
        "subcategories": [
            "Idli", "Dosa", "Pongal", "Upma", "Poori", "Paratha",
            "Breakfast Sandwiches", "Pancakes", "Waffles",
        ],
    },
    {
        "name": "Snacks", "emoji": "🥨", "display_order": 22,
        "subcategories": [
            "Chaat", "Samosa", "Puffs", "Pakoda", "Bajji", "Rolls", "Snack Momos",
        ],
    },
    {
        "name": "Bakery", "emoji": "🥐", "display_order": 23,
        "subcategories": [
            "Bread", "Buns", "Cookies", "Muffins", "Croissants",
        ],
    },
    {
        "name": "Cakes", "emoji": "🎂", "display_order": 24,
        "subcategories": [
            "Birthday Cakes", "Designer Cakes", "Wedding Cakes", "Cupcakes",
        ],
    },
    {
        "name": "Desserts", "emoji": "🍰", "display_order": 25,
        "subcategories": [
            "Brownies", "Cheesecakes", "Pastries", "Ice Cream", "Sundaes", "Traditional Sweets",
        ],
    },
    {
        "name": "Ice Cream", "emoji": "🍦", "display_order": 26,
        "subcategories": [
            "Gelato", "Kulfi", "Ice Cream Sundaes", "Ice Cream Cakes",
        ],
    },
    {
        "name": "Beverages", "emoji": "🥤", "display_order": 27,
        "subcategories": [
            "Tea", "Coffee", "Milkshakes", "Smoothies",
            "Juices", "Mocktails", "Soft Drinks", "Energy Drinks",
        ],
    },
    {
        "name": "Street Food", "emoji": "🛺", "display_order": 28,
        "subcategories": [
            "Pani Puri", "Bhel Puri", "Pav Bhaji", "Vada Pav", "Kathi Rolls", "Chaats",
        ],
    },
    {
        "name": "Rolls & Wraps", "emoji": "🌯", "display_order": 29,
        "subcategories": [
            "Kathi Rolls", "Shawarma Rolls", "Chicken Rolls", "Paneer Rolls",
        ],
    },
    {
        "name": "Momos", "emoji": "🥟", "display_order": 30,
        "subcategories": [
            "Veg Momos", "Chicken Momos", "Fried Momos", "Tandoori Momos",
        ],
    },
    {
        "name": "Kids Specials", "emoji": "🧒", "display_order": 31,
        "subcategories": [
            "Kids Meals", "Mini Burgers", "Mini Pizza", "Kids Nuggets",
        ],
    },
    {
        "name": "Premium Dining", "emoji": "💎", "display_order": 32,
        "subcategories": [
            "Fine Dining", "Chef Specials", "Signature Dishes",
        ],
    },
    {
        "name": "Festival Specials", "emoji": "🎊", "display_order": 33,
        "subcategories": [
            "Diwali Specials", "Ramzan Specials", "Christmas Specials", "Pongal Specials",
        ],
    },
    {
        "name": "Combo Meals", "emoji": "🍱", "display_order": 34,
        "subcategories": [
            "Family Packs", "Party Packs", "Value Meals", "Bucket Meals",
        ],
    },
    {
        "name": "Trending Categories", "emoji": "📈", "display_order": 35,
        "subcategories": [
            "Bestsellers", "Most Ordered", "New Arrivals", "Recommended", "Top Rated",
        ],
    },
    {
        "name": "Late Night Food", "emoji": "🌙", "display_order": 36,
        "subcategories": [
            "Midnight Biryani", "Midnight Snacks", "Midnight Desserts", "24/7 Food",
        ],
    },
    {
        "name": "Regional Indian Specials", "emoji": "🗺️", "display_order": 37,
        "subcategories": [
            "Ambur Biryani", "Dindigul Biryani", "Kolkata Biryani", "Lucknow Biryani",
            "Malabar Cuisine", "Coorg Cuisine", "Konkan Cuisine",
        ],
    },
    {
        "name": "Cloud Kitchen Specials", "emoji": "☁️", "display_order": 38,
        "subcategories": [
            "Virtual Brands", "Delivery Only Kitchens",
        ],
    },
    {
        "name": "Seasonal Specials", "emoji": "🌸", "display_order": 39,
        "subcategories": [
            "Summer Specials", "Winter Specials", "Monsoon Specials",
        ],
    },
]


def run():
    created_parents = 0
    created_subs = 0
    updated = 0

    for i, cat_data in enumerate(CATEGORIES):
        parent_obj, was_created = Category.objects.update_or_create(
            name=cat_data["name"],
            defaults={
                "emoji": cat_data.get("emoji", ""),
                "display_order": cat_data.get("display_order", i + 1),
                "is_active": True,
                "parent": None,
            },
        )
        if was_created:
            created_parents += 1
        else:
            updated += 1

        for j, sub_name in enumerate(cat_data.get("subcategories", [])):
            sub_obj, sub_created = Category.objects.update_or_create(
                name=sub_name,
                defaults={
                    "emoji": "",
                    "display_order": j + 1,
                    "is_active": True,
                    "parent": parent_obj,
                },
            )
            if sub_created:
                created_subs += 1
            else:
                updated += 1

    total = created_parents + created_subs
    print("Done!")
    print(f"   Parent categories created : {created_parents}")
    print(f"   Subcategories created     : {created_subs}")
    print(f"   Updated (already existed) : {updated}")
    print(f"   Total categories in DB    : {Category.objects.count()}")


if __name__ == "__main__":
    run()

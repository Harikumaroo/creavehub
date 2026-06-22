"""
Seed data for all remaining CraveHub modules:
Instamart, Dining, Party Orders, Gifts, Catering
"""
import os, sys, random, django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()

from restaurants.models import Restaurant
from instamart.models import InstamartCategory, InstamartStore, InstamartProduct
from dining.models import DiningVenue
from gifts.models import GiftCard
from parties.models import PartyPackage
from catering.models import CateringMenu

print("=== Seeding all modules ===")

# ─── INSTAMART ───────────────────────────────────────────
INSTAMART_CATEGORIES = [
    "Fruits & Vegetables", "Dairy & Bread", "Snacks & Munchies",
    "Cold Drinks & Juices", "Instant & Frozen", "Tea, Coffee & More",
    "Bakery & Biscuits", "Sweet Tooth", "Atta, Rice & Dal",
    "Dry Fruits, Masala & Oil", "Cleaning Essentials", "Personal Care",
    "Baby Care", "Pet Care", "Meat, Fish & Eggs",
]

for i, name in enumerate(INSTAMART_CATEGORIES):
    InstamartCategory.objects.get_or_create(name=name, defaults={"display_order": i})

print(f"  Instamart categories: {InstamartCategory.objects.count()}")

STORE_DATA = [
    {"name": "CraveHub Express - Anna Nagar",   "city": "Chennai", "address": "12 2nd Ave, Anna Nagar, Chennai", "pincode": "600040"},
    {"name": "CraveHub Express - T Nagar",       "city": "Chennai", "address": "45 Usman Rd, T Nagar, Chennai",   "pincode": "600017"},
    {"name": "CraveHub Express - Velachery",     "city": "Chennai", "address": "78 Velachery Main Rd, Chennai",   "pincode": "600042"},
    {"name": "CraveHub Express - Adyar",         "city": "Chennai", "address": "23 Adyar Main Rd, Chennai",       "pincode": "600020"},
    {"name": "CraveHub Express - Mylapore",      "city": "Chennai", "address": "56 Mylapore, Chennai",            "pincode": "600004"},
]

stores = []
for sd in STORE_DATA:
    s, _ = InstamartStore.objects.get_or_create(name=sd["name"], defaults={
        "city": sd["city"], "address": sd["address"], "pincode": sd["pincode"],
        "delivery_time": random.choice([8, 10, 12, 15]),
        "delivery_fee": random.choice([0, 15, 25]),
        "is_open": True, "is_active": True,
    })
    stores.append(s)

print(f"  Instamart stores: {len(stores)}")

PRODUCTS = {
    "Fruits & Vegetables": [
        ("Fresh Bananas", "1 dozen", 40), ("Red Tomatoes", "500g", 25), ("Onions", "1 kg", 35),
        ("Potatoes", "1 kg", 30), ("Green Capsicum", "250g", 20), ("Carrots", "500g", 35),
        ("Cucumber", "500g", 18), ("Apples", "4 pcs", 120), ("Mangoes", "1 kg", 80),
        ("Spinach", "250g", 15), ("Green Chilli", "100g", 10), ("Lemon", "4 pcs", 12),
    ],
    "Dairy & Bread": [
        ("Amul Toned Milk", "1 L", 58), ("Amul Butter", "100g", 52), ("Curd", "400g", 30),
        ("Paneer", "200g", 80), ("Cheese Slices", "200g", 95), ("Brown Bread", "400g", 40),
        ("White Bread", "400g", 35), ("Eggs", "6 pcs", 42), ("Greek Yogurt", "200g", 65),
    ],
    "Snacks & Munchies": [
        ("Lay's Classic Salted", "52g", 20), ("Kurkure Masala Munch", "75g", 20), ("Haldiram's Bhujia", "200g", 55),
        ("Pringles Original", "107g", 149), ("Doritos", "72g", 30), ("Trail Mix", "200g", 180),
        ("Popcorn", "80g", 40), ("Roasted Peanuts", "200g", 45), ("Nachos", "150g", 99),
    ],
    "Cold Drinks & Juices": [
        ("Coca-Cola", "750ml", 38), ("Pepsi", "750ml", 38), ("Sprite", "750ml", 38),
        ("Real Mango Juice", "1L", 99), ("Tropicana Mixed Fruit", "1L", 99), ("Sting Energy", "250ml", 20),
        ("Red Bull", "250ml", 125), ("Coconut Water", "200ml", 30), ("Frooti", "200ml", 10),
    ],
    "Instant & Frozen": [
        ("Maggi Noodles", "4 pack", 48), ("Top Ramen", "4 pack", 40), ("Frozen Peas", "500g", 50),
        ("Frozen Parathas", "5 pcs", 65), ("Cup Noodles", "70g", 40), ("Ready Biryani", "250g", 99),
        ("Frozen Momos", "10 pcs", 80), ("Instant Poha", "200g", 35), ("Oats", "500g", 99),
    ],
    "Tea, Coffee & More": [
        ("Tata Tea Gold", "250g", 120), ("Nescafe Classic", "50g", 145), ("Bru Instant", "50g", 99),
        ("Green Tea", "25 bags", 110), ("Chai Masala", "50g", 45), ("Filter Coffee", "200g", 150),
    ],
    "Bakery & Biscuits": [
        ("Britannia Good Day", "120g", 30), ("Parle-G", "250g", 22), ("Oreo", "120g", 30),
        ("Hide & Seek", "120g", 30), ("Bourbon", "120g", 25), ("Cake Rusk", "200g", 40),
        ("Croissant", "2 pcs", 60), ("Muffin", "1 pc", 45),
    ],
    "Sweet Tooth": [
        ("Dairy Milk Silk", "60g", 80), ("KitKat", "37g", 30), ("5 Star", "25g", 10),
        ("Gulab Jamun Mix", "200g", 65), ("Rasgulla", "500g", 110), ("Halwa", "250g", 85),
        ("Jalebi", "250g", 70), ("Soan Papdi", "250g", 60),
    ],
    "Atta, Rice & Dal": [
        ("Aashirvaad Atta", "5 kg", 265), ("India Gate Basmati", "1 kg", 110), ("Toor Dal", "1 kg", 130),
        ("Moong Dal", "1 kg", 110), ("Sona Masoori Rice", "5 kg", 320), ("Chana Dal", "1 kg", 95),
        ("Idli Rice", "1 kg", 55), ("Urad Dal", "500g", 80),
    ],
    "Dry Fruits, Masala & Oil": [
        ("Almonds", "200g", 180), ("Cashews", "200g", 210), ("Fortune Sunflower Oil", "1L", 140),
        ("MDH Chilli Powder", "100g", 45), ("Turmeric Powder", "100g", 30), ("Garam Masala", "50g", 40),
        ("Olive Oil", "500ml", 350), ("Raisins", "200g", 80),
    ],
    "Cleaning Essentials": [
        ("Vim Bar", "200g", 18), ("Harpic", "500ml", 89), ("Surf Excel", "1 kg", 120),
        ("Colin Glass Cleaner", "500ml", 75), ("Lizol", "500ml", 99), ("Scotch-Brite Pad", "3 pcs", 30),
    ],
    "Personal Care": [
        ("Dove Soap", "100g", 48), ("Head & Shoulders", "180ml", 180), ("Colgate", "150g", 80),
        ("Dettol Handwash", "200ml", 55), ("Nivea Cream", "60ml", 110), ("Vaseline", "100ml", 85),
    ],
    "Meat, Fish & Eggs": [
        ("Chicken Breast", "500g", 200), ("Mutton", "500g", 450), ("Fish Fillet", "250g", 180),
        ("Prawns", "250g", 250), ("Country Eggs", "12 pcs", 72), ("Chicken Drumstick", "500g", 170),
    ],
}

prod_count = 0
cats = {c.name: c for c in InstamartCategory.objects.all()}
for cat_name, prods in PRODUCTS.items():
    cat = cats.get(cat_name)
    if not cat:
        continue
    for store in stores:
        for pname, unit, price in prods:
            dp = round(price * 0.85, 0) if random.random() < 0.3 else None
            _, created = InstamartProduct.objects.get_or_create(
                store=store, name=pname, unit=unit,
                defaults={
                    "category": cat, "price": price, "discount_price": dp,
                    "stock": random.randint(5, 200), "is_available": True,
                    "is_featured": random.random() < 0.15,
                    "description": f"Fresh {pname} - {unit}",
                    "brand": random.choice(["", "Amul", "Tata", "Britannia", "ITC", "HUL", "Local Farm"]),
                }
            )
            if created:
                prod_count += 1

print(f"  Instamart products created: {prod_count}")

# ─── DINING ──────────────────────────────────────────────
restaurants = list(Restaurant.objects.filter(is_active=True, is_deleted=False)[:15])
dining_count = 0
for r in restaurants:
    _, created = DiningVenue.objects.get_or_create(restaurant=r, defaults={
        "seating_capacity": random.choice([30, 50, 80, 100, 150]),
        "has_ac": random.random() > 0.2,
        "has_outdoor": random.random() > 0.6,
        "avg_cost_for_two": random.choice([300, 500, 700, 900, 1200, 1500]),
        "is_active": True,
    })
    if created:
        dining_count += 1

print(f"  Dining venues created: {dining_count}")

# ─── GIFT CARDS ──────────────────────────────────────────
GIFT_CARDS = [
    {"name": "Birthday Treat",       "description": "Send a delicious birthday surprise!", "amount": 500, "image": "https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=400&h=300&fit=crop"},
    {"name": "Thank You",            "description": "Show gratitude with a food gift card", "amount": 300, "image": "https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=400&h=300&fit=crop"},
    {"name": "Celebration Pack",     "description": "Perfect for any celebration!",       "amount": 1000, "image": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=400&h=300&fit=crop"},
    {"name": "Foodie Delight",       "description": "For the food lover in your life",    "amount": 750, "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop"},
    {"name": "Festival Special",     "description": "Celebrate festivals with great food","amount": 1500, "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop"},
    {"name": "Love & Food",          "description": "Express love through food",          "amount": 500, "image": "https://images.unsplash.com/photo-1529566652340-2c41a1eb6d93?w=400&h=300&fit=crop"},
    {"name": "Quick Bite",           "description": "A small treat for someone special",  "amount": 200, "image": "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=400&h=300&fit=crop"},
    {"name": "Grand Feast",          "description": "Go big with this premium gift card", "amount": 2000, "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=300&fit=crop"},
]

gift_count = 0
for gc in GIFT_CARDS:
    _, created = GiftCard.objects.get_or_create(name=gc["name"], defaults=gc)
    if created:
        gift_count += 1

print(f"  Gift cards created: {gift_count}")

# ─── PARTY PACKAGES ─────────────────────────────────────
PARTY_NAMES = [
    ("Birthday Bash Veg",        True,  250),
    ("Birthday Bash Non-Veg",    False, 350),
    ("House Party Lite",         True,  200),
    ("House Party Premium",      False, 450),
    ("Corporate Lunch Veg",      True,  300),
    ("Corporate Lunch Non-Veg",  False, 400),
    ("Wedding Feast Veg",        True,  500),
    ("Wedding Feast Non-Veg",    False, 650),
    ("Kids Party Special",       True,  180),
    ("Weekend Brunch",           False, 350),
]

party_count = 0
for r in restaurants[:8]:
    for pname, is_veg, price in PARTY_NAMES:
        _, created = PartyPackage.objects.get_or_create(
            restaurant=r, name=pname,
            defaults={
                "description": f"A wonderful {pname.lower()} package from {r.name}. Includes starters, mains, desserts and beverages.",
                "min_guests": random.choice([10, 15, 20]),
                "max_guests": random.choice([50, 100, 200, 500]),
                "price_per_person": price + random.randint(-30, 30),
                "is_veg": is_veg,
                "is_active": True,
            }
        )
        if created:
            party_count += 1

print(f"  Party packages created: {party_count}")

# ─── CATERING MENUS ──────────────────────────────────────
CATERING_ITEMS = [
    ("South Indian Thali",          "Full meals with rice, sambar, rasam, poriyal, curd, payasam",      True,  150, "South Indian"),
    ("North Indian Thali",          "Dal, roti, paneer, rice, raita, gulab jamun",                      True,  180, "North Indian"),
    ("Non-Veg Grand Feast",         "Biryani, kebabs, chicken curry, dessert, drinks",                  False, 350, "Multi-Cuisine"),
    ("Chinese Buffet",              "Noodles, fried rice, manchurian, spring rolls, soup",              True,  200, "Chinese"),
    ("Continental Spread",          "Pasta, pizza, salads, soup, garlic bread, dessert",                True,  250, "Continental"),
    ("Biryani Box",                 "Hyderabadi biryani with raita, salan, and dessert",                False, 180, "Hyderabadi"),
    ("Street Food Counter",         "Pani puri, bhel, dosa, vada pav, chaat, juices",                  True,  120, "Street Food"),
    ("Premium Wedding Menu",        "5-course meal with live counters and dessert bar",                 False, 500, "Multi-Cuisine"),
    ("Breakfast Buffet",            "Idli, dosa, upma, pongal, vada, coffee, juice",                   True,  100, "South Indian"),
    ("BBQ & Grill",                 "Tandoori chicken, paneer tikka, kebabs, naan, biryani",           False, 400, "Mughlai"),
]

catering_count = 0
for r in restaurants[:10]:
    for cname, desc, is_veg, price, cuisine in CATERING_ITEMS:
        _, created = CateringMenu.objects.get_or_create(
            restaurant=r, name=cname,
            defaults={
                "description": desc,
                "price_per_plate": price + random.randint(-20, 20),
                "min_plates": random.choice([25, 50, 75, 100]),
                "cuisine_type": cuisine,
                "is_veg": is_veg,
                "is_active": True,
            }
        )
        if created:
            catering_count += 1

print(f"  Catering menus created: {catering_count}")

print("\n=== All modules seeded successfully! ===")

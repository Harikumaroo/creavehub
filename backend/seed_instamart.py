import os
import django
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from instamart.models import InstamartCategory, InstamartStore, InstamartProduct

def seed():
    print("Seeding Instamart Data...")

    # 1. Create Categories
    categories_data = [
        {"name": "Fruits & Vegetables", "image": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400&q=80"},
        {"name": "Dairy & Bread", "image": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&q=80"},
        {"name": "Snacks & Munchies", "image": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80"},
        {"name": "Cold Drinks & Juices", "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&q=80"},
        {"name": "Instant & Frozen", "image": "https://images.unsplash.com/photo-1606851181198-4b4a00dc0f5a?w=400&q=80"},
        {"name": "Tea, Coffee & More", "image": "https://images.unsplash.com/photo-1559525839-b184a4d698c7?w=400&q=80"},
        {"name": "Bakery & Biscuits", "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&q=80"},
        {"name": "Sweet Tooth", "image": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&q=80"},
        {"name": "Atta, Rice & Dal", "image": "https://images.unsplash.com/photo-1586201375761-83865001e8ac?w=400&q=80"},
        {"name": "Dry Fruits, Masala & Oil", "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400&q=80"},
        {"name": "Cleaning Essentials", "image": "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=400&q=80"},
        {"name": "Personal Care", "image": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&q=80"},
    ]

    categories = {}
    for i, c_data in enumerate(categories_data):
        cat, _ = InstamartCategory.objects.get_or_create(
            name=c_data["name"],
            defaults={"image": c_data["image"], "display_order": i}
        )
        categories[cat.name] = cat
        print(f"Added Category: {cat.name}")

    # 2. Create Store
    store, _ = InstamartStore.objects.get_or_create(
        name="CraveHub Instamart Central",
        defaults={
            "address": "123 Delivery Hub, Main Street",
            "city": "Chennai",
            "pincode": "600001",
            "delivery_time": 10,
            "is_open": True,
            "is_active": True
        }
    )
    print(f"Added Store: {store.name}")

    # 3. Create Products
    products_data = [
        # Fruits & Veg
        ("Onion (Pyaz)", "Fruits & Vegetables", 45.0, 39.0, "1 kg", "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400&q=80"),
        ("Tomato - Local", "Fruits & Vegetables", 30.0, 25.0, "500 g", "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&q=80"),
        ("Potato", "Fruits & Vegetables", 40.0, None, "1 kg", "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&q=80"),
        ("Fresh Coriander Leaves", "Fruits & Vegetables", 15.0, None, "100 g", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400&q=80"),
        ("Green Chilli", "Fruits & Vegetables", 20.0, 16.0, "100 g", "https://images.unsplash.com/photo-1585238263595-df7201b1a039?w=400&q=80"),
        ("Lemon", "Fruits & Vegetables", 30.0, 24.0, "250 g", "https://images.unsplash.com/photo-1590502593747-42a996fd6bc1?w=400&q=80"),
        ("Banana - Robusta", "Fruits & Vegetables", 60.0, 52.0, "1 kg", "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400&q=80"),
        
        # Dairy & Bread
        ("Amul Taaza Toned Milk", "Dairy & Bread", 54.0, None, "1 L", "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80"),
        ("Nandini GoodLife Double Toned Milk", "Dairy & Bread", 50.0, None, "1 L", "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80"),
        ("Amul Butter - Pasteurized", "Dairy & Bread", 58.0, None, "100 g", "https://images.unsplash.com/photo-1589985270826-4b7bb135ba9d?w=400&q=80"),
        ("Milky Mist Paneer", "Dairy & Bread", 95.0, 89.0, "200 g", "https://images.unsplash.com/photo-1631451095764-16a7f11c750e?w=400&q=80"),
        ("Modern Sandwich Bread", "Dairy & Bread", 40.0, 35.0, "400 g", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&q=80"),
        ("Eggs - White", "Dairy & Bread", 48.0, 42.0, "6 pcs", "https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=400&q=80"),

        # Snacks & Munchies
        ("Lays India's Magic Masala", "Snacks & Munchies", 20.0, None, "50 g", "https://images.unsplash.com/photo-1566478989037-e988229b4e7f?w=400&q=80"),
        ("Haldiram's Bhujia Sev", "Snacks & Munchies", 110.0, 105.0, "400 g", "https://images.unsplash.com/photo-1604328698692-f76ea9498e76?w=400&q=80"),
        ("Doritos Nacho Cheese", "Snacks & Munchies", 50.0, 45.0, "100 g", "https://images.unsplash.com/photo-1613919113640-25732cea5e79?w=400&q=80"),
        ("Kurkure Masala Munch", "Snacks & Munchies", 20.0, None, "90 g", "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80"),

        # Cold Drinks
        ("Coca-Cola", "Cold Drinks & Juices", 40.0, 38.0, "750 ml", "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&q=80"),
        ("Thums Up", "Cold Drinks & Juices", 40.0, 38.0, "750 ml", "https://images.unsplash.com/photo-1581006852262-e4307cf6283a?w=400&q=80"),
        ("Sprite", "Cold Drinks & Juices", 40.0, 35.0, "750 ml", "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=400&q=80"),
        ("Red Bull Energy Drink", "Cold Drinks & Juices", 125.0, 115.0, "250 ml", "https://images.unsplash.com/photo-1579893963473-8a30f3408f9c?w=400&q=80"),

        # Instant & Frozen
        ("Maggi 2-Minute Noodles", "Instant & Frozen", 14.0, None, "70 g", "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400&q=80"),
        ("McCain French Fries", "Instant & Frozen", 150.0, 120.0, "400 g", "https://images.unsplash.com/photo-1573080496219-bb080e72221b?w=400&q=80"),
        ("Yippee Magic Masala Noodles", "Instant & Frozen", 12.0, None, "60 g", "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=400&q=80"),

        # Cleaning Essentials
        ("Surf Excel Easy Wash Detergent", "Cleaning Essentials", 130.0, 118.0, "1 kg", "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=400&q=80"),
        ("Vim Dishwash Liquid", "Cleaning Essentials", 115.0, 105.0, "500 ml", "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=400&q=80"),
        ("Harpic Toilet Cleaner", "Cleaning Essentials", 99.0, 91.0, "500 ml", "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=400&q=80"),

        # Personal Care
        ("Colgate MaxFresh Toothpaste", "Personal Care", 110.0, 95.0, "150 g", "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&q=80"),
        ("Dettol Original Soap", "Personal Care", 45.0, 42.0, "125 g", "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400&q=80"),
        ("Dove Deep Moisture Body Wash", "Personal Care", 200.0, 160.0, "250 ml", "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400&q=80"),
        
        # Sweet Tooth
        ("Cadbury Dairy Milk Silk", "Sweet Tooth", 80.0, 75.0, "60 g", "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=400&q=80"),
        ("Kwality Wall's Cornetto", "Sweet Tooth", 40.0, None, "120 ml", "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&q=80"),
    ]

    for name, cat_name, price, discount_price, unit, image in products_data:
        cat = categories.get(cat_name)
        if not cat: continue
        
        p, created = InstamartProduct.objects.get_or_create(
            store=store,
            name=name,
            defaults={
                "category": cat,
                "price": Decimal(str(price)),
                "discount_price": Decimal(str(discount_price)) if discount_price else None,
                "unit": unit,
                "image": image,
                "stock": random.randint(50, 200),
                "is_available": True,
                "is_featured": random.choice([True, False, False])
            }
        )
        if created:
            print(f"Added Product: {name}")

    print(f"Finished seeding Instamart! Total Products: {InstamartProduct.objects.count()}")

if __name__ == "__main__":
    seed()

import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from instamart.models import InstamartCategory, InstamartStore, InstamartProduct

data = {
    "Grocery & Staples": ["Rice", "Atta & Flour", "Dal & Pulses", "Cooking Oil", "Sugar & Jaggery", "Salt", "Spices & Masalas", "Dry Fruits", "Nuts & Seeds", "Ghee", "Vinegar & Sauces", "Pickles", "Baking Essentials", "Instant Mixes", "Breakfast Cereals"],
    "Fruits & Vegetables": ["Fresh Fruits", "Fresh Vegetables", "Leafy Greens", "Exotic Fruits", "Exotic Vegetables", "Fresh Cuts", "Organic Produce", "Herbs & Seasonings"],
    "Dairy, Bread & Eggs": ["Milk", "Curd/Yogurt", "Paneer", "Cheese", "Butter", "Ghee", "Bread", "Eggs", "Cream", "Milkshakes", "Dairy Drinks"],
    "Snacks & Munchies": ["Chips", "Namkeen", "Biscuits", "Chocolates", "Cookies", "Popcorn", "Energy Bars", "Instant Snacks", "Traditional Snacks"],
    "Beverages": ["Soft Drinks", "Juices", "Energy Drinks", "Tea", "Coffee", "Health Drinks", "Water", "Coconut Water", "Milk-Based Beverages"],
    "Instant & Ready-to-Eat": ["Noodles", "Pasta", "Soups", "Frozen Snacks", "Ready Meals", "Ready-to-Cook Mixes", "Frozen Foods"],
    "Personal Care": ["Shampoo", "Conditioner", "Soap", "Face Wash", "Skin Care", "Hair Care", "Oral Care", "Deodorants", "Perfumes", "Men's Grooming", "Women's Hygiene"],
    "Home & Cleaning": ["Detergents", "Dishwash", "Floor Cleaners", "Toilet Cleaners", "Garbage Bags", "Air Fresheners", "Cleaning Tools", "Tissue & Paper Products"],
    "Baby Care": ["Diapers", "Baby Food", "Baby Wipes", "Baby Shampoo", "Baby Soap", "Baby Powder", "Feeding Essentials"],
    "Pet Care": ["Dog Food", "Cat Food", "Pet Treats", "Pet Accessories", "Pet Hygiene Products"],
    "Health & Wellness": ["Vitamins", "Protein Supplements", "Health Drinks", "First Aid", "Medical Essentials", "Ayurvedic Products", "Immunity Boosters"],
    "Electronics & Accessories": ["Mobile Chargers", "Earphones", "Batteries", "Power Banks", "Bulbs", "Extension Boards", "Smart Gadgets"],
    "Kitchen & Home Essentials": ["Kitchen Tools", "Choppers", "Containers", "Cookware", "Storage Boxes", "Water Bottles", "Dining Essentials"],
    "Stationery & Office": ["Pens", "Pencils", "Notebooks", "Printer Paper", "Office Supplies"],
    "Pooja & Festive": ["Agarbatti", "Camphor", "Diyas", "Flowers", "Pooja Kits", "Festival Decor"]
}

category_images = {
    "Grocery & Staples": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&q=80",
    "Fruits & Vegetables": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400&q=80",
    "Dairy, Bread & Eggs": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&q=80",
    "Snacks & Munchies": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=400&q=80",
    "Beverages": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&q=80",
    "Instant & Ready-to-Eat": "https://images.unsplash.com/photo-1606851181198-4b4a00dc0f5a?w=400&q=80",
    "Personal Care": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&q=80",
    "Home & Cleaning": "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=400&q=80",
    "Baby Care": "https://images.unsplash.com/photo-1519689680058-324335c77eba?w=400&q=80",
    "Pet Care": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400&q=80",
    "Health & Wellness": "https://images.unsplash.com/photo-1584308666744-24d5e4b17849?w=400&q=80",
    "Electronics & Accessories": "https://images.unsplash.com/photo-1550009158-9efff6c65e8a?w=400&q=80",
    "Kitchen & Home Essentials": "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400&q=80",
    "Stationery & Office": "https://images.unsplash.com/photo-1456735190827-d1262f71b8a3?w=400&q=80",
    "Pooja & Festive": "https://images.unsplash.com/photo-1605335198285-802c6b459426?w=400&q=80"
}

def seed_extra():
    store = InstamartStore.objects.first()
    if not store:
        store = InstamartStore.objects.create(
            name="CraveHub Instamart Central",
            address="123 Delivery Hub, Main Street",
            city="Chennai",
            pincode="600001",
            delivery_time=10,
            is_open=True,
            is_active=True
        )

    for i, (cat_name, items) in enumerate(data.items()):
        image = category_images.get(cat_name, "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&q=80")
        cat, created = InstamartCategory.objects.get_or_create(
            name=cat_name,
            defaults={"image": image, "display_order": i + 20}
        )
        if created:
            print(f"Added Category: {cat_name}")

        for item_name in items:
            price = random.randint(30, 500)
            discount_price = price - random.randint(5, int(price*0.2)) if random.random() > 0.5 else None
            
            p, created = InstamartProduct.objects.get_or_create(
                store=store,
                name=item_name,
                category=cat,
                defaults={
                    "price": Decimal(str(price)),
                    "discount_price": Decimal(str(discount_price)) if discount_price else None,
                    "unit": "1 pc",
                    "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&q=80",
                    "stock": random.randint(10, 100),
                    "is_available": True,
                    "is_featured": random.choice([True, False, False])
                }
            )
            if created:
                print(f"Added Product: {item_name}")

if __name__ == "__main__":
    seed_extra()
    print("Done adding extra items!")

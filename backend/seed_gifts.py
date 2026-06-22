import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from instamart.models import InstamartCategory, InstamartStore, InstamartProduct

def seed_gifts():
    print("Seeding Swiggy Gifts UI Mockup Data...")

    # Create the Gift Store
    store, created = InstamartStore.objects.get_or_create(
        name="Swiggy Gifts Hub",
        defaults={
            "address": "123 Gift Avenue",
            "city": "Chennai",
            "pincode": "600001",
            "delivery_time": 30,
            "delivery_fee": 40.00,
            "minimum_order": 100.00,
            "is_open": True,
            "is_active": True,
            "image": "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=800&q=80"
        }
    )

    categories_data = {
        "From the Florist": [
            {
                "name": "Pink Roses Bouquet",
                "description": "FNP Cakes By Ferns N Petals",
                "price": 499,
                "discount_price": None,
                "image": "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=400&q=80",
                "delivery_time": "35 MINS",
                "rating": 4.3,
                "rating_count": "748",
            },
            {
                "name": "KYARI Jade Plant in Self Watering Green...",
                "description": "KYARI",
                "price": 299,
                "discount_price": 128,
                "image": "https://images.unsplash.com/photo-1459156212016-c812468e2115?w=400&q=80",
                "delivery_time": "14 MINS",
                "rating": None,
                "rating_count": None,
            }
        ],
        "Most Gifted": [
            {
                "name": "Eggless Choco Truffle Cake (500g)",
                "description": "SMOOR",
                "price": 729,
                "discount_price": None,
                "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80",
                "delivery_time": "20 MINS",
                "rating": 4.7,
                "rating_count": "2.4K+",
            },
            {
                "name": "Toyshine Fastest Finger Hockey Puck ...",
                "description": "Toyshine",
                "price": 599,
                "discount_price": 369,
                "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&q=80",
                "delivery_time": "14 MINS",
                "rating": 4.3,
                "rating_count": "2K",
            }
        ],
        "Unique Finds": [
            {
                "name": "Bartique Stainless Steel Home ...",
                "description": "Bartique",
                "price": 2299,
                "discount_price": 2049,
                "image": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400&q=80",
                "delivery_time": "30 MINS",
                "rating": None,
                "rating_count": None,
            }
        ],
        "Chains & Necklaces": [
            {
                "name": "NVR Women's Gold-Plated Minimalist...",
                "description": "NVR",
                "price": 999,
                "discount_price": 99,
                "image": "https://images.unsplash.com/photo-1599643478524-fb66f70d00f8?w=400&q=80",
                "delivery_time": "14 MINS",
                "rating": 4,
                "rating_count": "770",
            },
            {
                "name": "MINUTIAE Gold Infinity Shape Pendant...",
                "description": "Minutiae",
                "price": 1999,
                "discount_price": 324,
                "image": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400&q=80",
                "delivery_time": "14 MINS",
                "rating": None,
                "rating_count": None,
            }
        ],
        "Cakes for Celebrations": [
            {
                "name": "Black Forest Cake",
                "description": "Bakingo",
                "price": 600,
                "discount_price": None,
                "image": "https://images.unsplash.com/photo-1557308536-ee471ef2c390?w=400&q=80",
                "delivery_time": "25 MINS",
                "rating": 4.5,
                "rating_count": "1.2K",
            }
        ],
        "Budget Friendly": [
             {
                "name": "Assorted Chocolates Box",
                "description": "Ferrero",
                "price": 300,
                "discount_price": None,
                "image": "https://images.unsplash.com/photo-1548883354-94cb1f0ab971?w=400&q=80",
                "delivery_time": "15 MINS",
                "rating": 4.8,
                "rating_count": "5K",
             }
        ],
        "Electronics & Gadgets": [
             {
                 "name": "Noise ColorFit Pulse 3 Smartwatch",
                 "description": "Noise",
                 "price": 2999,
                 "discount_price": 1499,
                 "image": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&q=80",
                 "delivery_time": "45 MINS",
                 "rating": 4.5,
                 "rating_count": "12K",
             },
             {
                 "name": "Boat Airdopes 141 True Wireless Earbuds",
                 "description": "boAt",
                 "price": 4490,
                 "discount_price": 1299,
                 "image": "https://images.unsplash.com/photo-1572569438068-4098ed2a44ea?w=400&q=80",
                 "delivery_time": "30 MINS",
                 "rating": 4.2,
                 "rating_count": "54K",
             }
        ],
        "Home Decor": [
             {
                 "name": "Webelkart Premium Metal Wall Art",
                 "description": "Webelkart",
                 "price": 3999,
                 "discount_price": 1699,
                 "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=400&q=80",
                 "delivery_time": "25 MINS",
                 "rating": 4.1,
                 "rating_count": "890",
             }
        ]
    }

    for cat_name, products in categories_data.items():
        cat_obj, _ = InstamartCategory.objects.get_or_create(
            name=cat_name,
            defaults={"is_active": True}
        )
        
        for p in products:
            price = Decimal(str(p["price"]))
            discount_price = Decimal(str(p["discount_price"])) if p["discount_price"] else None

            # Storing extra fields in description temporarily, or we just rely on UI mock values in frontend.
            InstamartProduct.objects.update_or_create(
                store=store,
                name=p["name"],
                category=cat_obj,
                defaults={
                    "description": p["description"], # using description as brand name to fit the UI mock
                    "image": p["image"],
                    "price": price,
                    "discount_price": discount_price,
                    "stock": 50,
                    "is_available": True
                }
            )

if __name__ == "__main__":
    seed_gifts()
    print("Gifts UI mockup data seeded successfully!")

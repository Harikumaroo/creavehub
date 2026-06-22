import os
import django
import random
import uuid
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from instamart.models import InstamartCategory, InstamartStore, InstamartProduct

def run():
    print("Seeding realistic gift items...")

    # Get a store
    store = InstamartStore.objects.first()
    if not store:
        print("No store found!")
        return

    # Delete existing products in gift categories to avoid mixing groceries
    gift_cat_names = [
        "From the Florist",
        "Cakes for Celebrations",
        "Most Gifted",
        "Premium Watches",
        "Jewelry & Perfumes"
    ]
    
    gift_products = InstamartProduct.objects.filter(category__name__in=gift_cat_names)
    print(f"Deleting {gift_products.count()} old mixed grocery/gift items...")
    gift_products.delete()

    # Create missing categories just in case
    for name in gift_cat_names:
        InstamartCategory.objects.get_or_create(name=name)

    cat_florist = InstamartCategory.objects.get(name="From the Florist")
    cat_cakes = InstamartCategory.objects.get(name="Cakes for Celebrations")
    cat_gifted = InstamartCategory.objects.get(name="Most Gifted")
    cat_watches = InstamartCategory.objects.get(name="Premium Watches")
    cat_jewelry = InstamartCategory.objects.get(name="Jewelry & Perfumes")

    new_items = [
        # Florist
        {"cat": cat_florist, "name": "Premium Red Roses Bouquet", "price": 899, "img": "https://images.unsplash.com/photo-1563241598-a24ce1e47323?w=800&q=80", "desc": "A stunning bouquet of 24 premium fresh red roses."},
        {"cat": cat_florist, "name": "Orchid & Lilies Arrangement", "price": 1299, "img": "https://images.unsplash.com/photo-1562690868-60bbe7293e94?w=800&q=80", "desc": "Elegant white orchids and pink lilies in a premium glass vase."},
        {"cat": cat_florist, "name": "Sunflower Sunshine Box", "price": 749, "img": "https://images.unsplash.com/photo-1597826368522-9f4cb5a6ba48?w=800&q=80", "desc": "Bright and cheerful sunflowers arranged in a wooden rustic box."},
        
        # Cakes
        {"cat": cat_cakes, "name": "Belgian Chocolate Truffle Cake (1kg)", "price": 1499, "img": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&q=80", "desc": "Rich, dense, and utterly delicious pure Belgian chocolate cake."},
        {"cat": cat_cakes, "name": "Fresh Fruit & Cream Cake (1kg)", "price": 1299, "img": "https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=800&q=80", "desc": "Vanilla sponge layered with fresh dairy cream and seasonal fruits."},
        {"cat": cat_cakes, "name": "Red Velvet Heart Cake", "price": 999, "img": "https://images.unsplash.com/photo-1586788224331-947f68671b1e?w=800&q=80", "desc": "A beautiful heart-shaped red velvet cake with cream cheese frosting."},
        
        # Most Gifted
        {"cat": cat_gifted, "name": "Gourmet Chocolates Box", "price": 1899, "img": "https://images.unsplash.com/photo-1548907040-4baa42d10919?w=800&q=80", "desc": "An assorted collection of 24 handcrafted artisanal chocolates."},
        {"cat": cat_gifted, "name": "Luxury Aromatic Candles Set", "price": 1199, "img": "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=800&q=80", "desc": "Set of 3 premium soy wax candles in lavender, vanilla, and sandalwood."},
        {"cat": cat_gifted, "name": "Personalized Leather Wallet", "price": 1599, "img": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&q=80", "desc": "Genuine leather minimalist wallet. (Customization available post-order)"},
        {"cat": cat_gifted, "name": "Cute Teddy Bear (Large)", "price": 999, "img": "https://images.unsplash.com/photo-1559454403-b8fb88521f11?w=800&q=80", "desc": "A 3-foot tall, super soft and huggable brown teddy bear."},

        # Watches
        {"cat": cat_watches, "name": "Men's Chronograph Steel Watch", "price": 4999, "img": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80", "desc": "Premium stainless steel analog watch with black dial."},
        {"cat": cat_watches, "name": "Women's Rose Gold Classic", "price": 3499, "img": "https://images.unsplash.com/photo-1508656966835-df4d9d10e6aa?w=800&q=80", "desc": "Elegant rose gold minimalist watch with a mesh strap."},
        
        # Jewelry & Perfumes
        {"cat": cat_jewelry, "name": "Swarovski Crystal Pendant", "price": 5499, "img": "https://images.unsplash.com/photo-1599643478524-fb66f70a0066?w=800&q=80", "desc": "A delicate silver chain with a sparkling teardrop crystal."},
        {"cat": cat_jewelry, "name": "Chanel No. 5 Eau De Parfum", "price": 12999, "img": "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&q=80", "desc": "The iconic and timeless fragrance for women."},
        {"cat": cat_jewelry, "name": "Dior Sauvage Men's Parfum", "price": 11499, "img": "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=800&q=80", "desc": "A radically fresh composition, both raw and noble."}
    ]

    for item in new_items:
        InstamartProduct.objects.create(
            store=store,
            category=item["cat"],
            name=item["name"],
            description=item["desc"],
            brand="CraveHub Gifts",
            image=item["img"],
            price=Decimal(item["price"]),
            stock=100,
            is_available=True,
            is_featured=True
        )

    print(f"Successfully added {len(new_items)} fresh gift items!")

if __name__ == '__main__':
    run()

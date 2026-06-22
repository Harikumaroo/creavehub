"""
CraveHub — Load Additional Offers Script
Run with: python manage.py shell < scripts/load_offers.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()

from offers.models import Offer

print("=" * 60)
print("  CraveHub — Loading Additional Offers")
print("=" * 60)

future_date = date.today() + timedelta(days=365)

offers_data = [
    # FOOD
    {"title": "Flat ₹50 Off on Food", "code": "FOOD50", "type": "FLAT", "val": "50.00", "min": "149.00", "max": None},
    {"title": "10% Off on Food Orders", "code": "FOOD10", "type": "PERCENTAGE", "val": "10.00", "min": "199.00", "max": "100.00"},
    {"title": "Foodie Feast - ₹100 Off", "code": "FEAST100", "type": "FLAT", "val": "100.00", "min": "499.00", "max": None},
    {"title": "20% Off Weekend Food", "code": "WEEKEND20", "type": "PERCENTAGE", "val": "20.00", "min": "399.00", "max": "150.00"},
    {"title": "Free Delivery on Food", "code": "FOODFREE", "type": "FREE_DELIVERY", "val": "50.00", "min": "249.00", "max": None},
    
    # INSTAMART
    {"title": "Flat ₹40 Off Groceries", "code": "INSTA40", "type": "FLAT", "val": "40.00", "min": "199.00", "max": None},
    {"title": "15% Off Instamart", "code": "INSTA15", "type": "PERCENTAGE", "val": "15.00", "min": "399.00", "max": "120.00"},
    {"title": "Free Delivery Groceries", "code": "INSTAFREE", "type": "FREE_DELIVERY", "val": "50.00", "min": "149.00", "max": None},
    {"title": "Flat ₹100 Off Instamart", "code": "INSTA100", "type": "FLAT", "val": "100.00", "min": "999.00", "max": None},
    {"title": "5% Off Daily Essentials", "code": "DAILY5", "type": "PERCENTAGE", "val": "5.00", "min": "99.00", "max": "50.00"},
    
    # DINING
    {"title": "Flat ₹200 Off Dining", "code": "DINE200", "type": "FLAT", "val": "200.00", "min": "999.00", "max": None},
    {"title": "15% Off Dining Out", "code": "DINE15", "type": "PERCENTAGE", "val": "15.00", "min": "1499.00", "max": "500.00"},
    {"title": "Flat ₹500 Off Dining", "code": "DINE500", "type": "FLAT", "val": "500.00", "min": "2999.00", "max": None},
    {"title": "10% Off Fine Dining", "code": "FINE10", "type": "PERCENTAGE", "val": "10.00", "min": "1999.00", "max": "300.00"},
    {"title": "Flat ₹100 Off Tables", "code": "TABLE100", "type": "FLAT", "val": "100.00", "min": "499.00", "max": None},
    
    # PARTY
    {"title": "Flat ₹500 Off Party", "code": "PARTY500", "type": "FLAT", "val": "500.00", "min": "3999.00", "max": None},
    {"title": "10% Off Party Orders", "code": "PARTY10", "type": "PERCENTAGE", "val": "10.00", "min": "4999.00", "max": "1000.00"},
    {"title": "Flat ₹1000 Off Big Party", "code": "PARTY1000", "type": "FLAT", "val": "1000.00", "min": "9999.00", "max": None},
    {"title": "5% Off Small Party", "code": "PARTY5", "type": "PERCENTAGE", "val": "5.00", "min": "1999.00", "max": "200.00"},
    {"title": "Flat ₹300 Off Gatherings", "code": "GATHER300", "type": "FLAT", "val": "300.00", "min": "2499.00", "max": None},
    
    # GIFTS
    {"title": "Flat ₹50 Off Gifts", "code": "GIFT50", "type": "FLAT", "val": "50.00", "min": "299.00", "max": None},
    {"title": "10% Off Gift Cards", "code": "GIFT10", "type": "PERCENTAGE", "val": "10.00", "min": "499.00", "max": "100.00"},
    {"title": "Flat ₹200 Off Premium Gifts", "code": "GIFT200", "type": "FLAT", "val": "200.00", "min": "1499.00", "max": None},
    {"title": "15% Off Surprise Gifts", "code": "SURPRISE15", "type": "PERCENTAGE", "val": "15.00", "min": "999.00", "max": "250.00"},
    {"title": "Flat ₹100 Off Hampers", "code": "HAMPER100", "type": "FLAT", "val": "100.00", "min": "799.00", "max": None},
    
    # CATERING
    {"title": "Flat ₹1000 Off Catering", "code": "CATER1000", "type": "FLAT", "val": "1000.00", "min": "9999.00", "max": None},
    {"title": "10% Off Catering Orders", "code": "CATER10", "type": "PERCENTAGE", "val": "10.00", "min": "14999.00", "max": "2000.00"},
    {"title": "Flat ₹2000 Off Weddings", "code": "CATER2000", "type": "FLAT", "val": "2000.00", "min": "24999.00", "max": None},
    {"title": "5% Off Corporate Catering", "code": "CORP5", "type": "PERCENTAGE", "val": "5.00", "min": "4999.00", "max": "1000.00"},
    {"title": "Flat ₹500 Off Small Events", "code": "EVENT500", "type": "FLAT", "val": "500.00", "min": "4999.00", "max": None},
]

total_created = 0
for o in offers_data:
    offer, created = Offer.objects.get_or_create(
        coupon_code=o["code"],
        defaults={
            "title": o["title"],
            "discount_type": o["type"],
            "discount_value": Decimal(o["val"]),
            "minimum_order_amount": Decimal(o["min"]),
            "maximum_discount": Decimal(o["max"]) if o["max"] else None,
            "expiry_date": future_date,
            "is_active": True,
        },
    )
    if created:
        total_created += 1
        print(f"  CREATED: {offer.coupon_code} — {offer.title}")
    else:
        print(f"  EXISTS: {offer.coupon_code} — {offer.title}")

print("\n" + "=" * 60)
print(f"  ✅ Added {total_created} new offers! Total offers: {Offer.objects.count()}")
print("=" * 60)

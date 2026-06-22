import os
import django
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()

from offers.models import Offer, DiscountType
from restaurants.models import Restaurant
from dining.models import DiningVenue

def seed_offers():
    print("Seeding mock offers...")
    
    # Create or update some base offers
    offer1, _ = Offer.objects.get_or_create(
        coupon_code="ONEEXCL20",
        defaults={
            "title": "Flat 20% off on Total Bill",
            "discount_type": DiscountType.PERCENTAGE,
            "discount_value": Decimal("20.00"),
            "expiry_date": timezone.now().date() + timedelta(days=30),
            "is_active": True
        }
    )
    
    offer2, _ = Offer.objects.get_or_create(
        coupon_code="DINE15",
        defaults={
            "title": "Flat 15% off",
            "discount_type": DiscountType.PERCENTAGE,
            "discount_value": Decimal("15.00"),
            "expiry_date": timezone.now().date() + timedelta(days=15),
            "is_active": True
        }
    )

    offer3, _ = Offer.objects.get_or_create(
        coupon_code="WALKIN100",
        defaults={
            "title": "₹100 Off Walk-in Special",
            "discount_type": DiscountType.FLAT,
            "discount_value": Decimal("100.00"),
            "minimum_order_amount": Decimal("500.00"),
            "expiry_date": timezone.now().date() + timedelta(days=7),
            "is_active": True
        }
    )
    
    offer4, _ = Offer.objects.get_or_create(
        coupon_code="WEEKEND50",
        defaults={
            "title": "50% Off Weekend Bonanza",
            "discount_type": DiscountType.PERCENTAGE,
            "discount_value": Decimal("50.00"),
            "maximum_discount": Decimal("250.00"),
            "expiry_date": timezone.now().date() + timedelta(days=2),
            "is_active": True
        }
    )

    offer5, _ = Offer.objects.get_or_create(
        coupon_code="FIRSTORDER",
        defaults={
            "title": "Flat ₹200 Off for New Foodies",
            "discount_type": DiscountType.FLAT,
            "discount_value": Decimal("200.00"),
            "minimum_order_amount": Decimal("499.00"),
            "expiry_date": timezone.now().date() + timedelta(days=60),
            "is_active": True
        }
    )

    offer6, _ = Offer.objects.get_or_create(
        coupon_code="LUNCH25",
        defaults={
            "title": "25% Off Power Lunch",
            "discount_type": DiscountType.PERCENTAGE,
            "discount_value": Decimal("25.00"),
            "maximum_discount": Decimal("150.00"),
            "expiry_date": timezone.now().date() + timedelta(days=14),
            "is_active": True
        }
    )

    offer7, _ = Offer.objects.get_or_create(
        coupon_code="PARTY500",
        defaults={
            "title": "Flat ₹500 Off on Party Orders",
            "discount_type": DiscountType.FLAT,
            "discount_value": Decimal("500.00"),
            "minimum_order_amount": Decimal("2000.00"),
            "expiry_date": timezone.now().date() + timedelta(days=45),
            "is_active": True
        }
    )
    
    # Get all active dining venues
    venues = DiningVenue.objects.filter(is_active=True).select_related("restaurant")
    
    if venues.exists():
        # Attach offer1 to first venue
        v1 = venues[0]
        offer1.restaurants.add(v1.restaurant)
        offer3.restaurants.add(v1.restaurant)
        print(f"Added ONEEXCL20 and WALKIN100 to {v1.restaurant.name}")
        
        if len(venues) > 1:
            v2 = venues[1]
            offer2.restaurants.add(v2.restaurant)
            print(f"Added DINE15 to {v2.restaurant.name}")
            
        # Add new offers globally to all venues so they appear everywhere
        for venue in venues:
            offer4.restaurants.add(venue.restaurant)
            offer5.restaurants.add(venue.restaurant)
            offer6.restaurants.add(venue.restaurant)
            offer7.restaurants.add(venue.restaurant)
        print("Added WEEKEND50, FIRSTORDER, LUNCH25, PARTY500 to all active restaurants!")
            
    print("Seeding complete.")

if __name__ == "__main__":
    seed_offers()

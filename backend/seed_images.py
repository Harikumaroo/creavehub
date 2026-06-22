import os
import django
import urllib.parse
from django.db.models import F

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from restaurants.models import Restaurant
from menu.models import MenuItem
from categories.models import Category
from instamart.models import InstamartCategory, InstamartStore, InstamartProduct
from parties.models import PartyPackage
from gifts.models import GiftCard
from catering.models import CateringMenu
from banners.models import Banner

import random

def get_image_url(name, context="food"):
    lock_id = random.randint(1, 100000)
    return f"https://loremflickr.com/800/600/{context}?lock={lock_id}"

def seed_images():
    print("Updating Restaurants...")
    for r in Restaurant.objects.all():
        r.cover_image = get_image_url(r.name, "restaurant")
        r.logo = get_image_url(r.name, "logo")
        r.save(update_fields=['cover_image', 'logo'])

    print("Updating Menu Items...")
    for m in MenuItem.objects.all():
        m.image = get_image_url(m.name, "food")
        m.save(update_fields=['image'])

    print("Updating Categories...")
    for c in Category.objects.all():
        c.image = get_image_url(c.name, "food")
        c.save(update_fields=['image'])

    print("Updating Instamart Categories...")
    for c in InstamartCategory.objects.all():
        c.image = get_image_url(c.name, "grocery")
        c.save(update_fields=['image'])

    print("Updating Instamart Stores...")
    for s in InstamartStore.objects.all():
        s.image = get_image_url(s.name, "store")
        s.save(update_fields=['image'])

    print("Updating Instamart Products...")
    for p in InstamartProduct.objects.all():
        p.image = get_image_url(p.name, "grocery")
        p.save(update_fields=['image'])

    print("Updating Party Packages...")
    for p in PartyPackage.objects.all():
        p.image = get_image_url(p.name, "party")
        p.save(update_fields=['image'])

    print("Updating Gift Cards...")
    for g in GiftCard.objects.all():
        g.image = get_image_url(g.name, "gift")
        g.save(update_fields=['image'])

    print("Updating Catering Menus...")
    for c in CateringMenu.objects.all():
        c.image = get_image_url(c.name, "catering")
        c.save(update_fields=['image'])

    print("Updating Banners...")
    for b in Banner.objects.all():
        b.image = get_image_url(b.title, "banner")
        b.save(update_fields=['image'])

    print("Done!")

if __name__ == "__main__":
    seed_images()

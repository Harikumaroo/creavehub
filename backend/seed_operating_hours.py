import os
import django
from datetime import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cravehub.settings')
django.setup()

from restaurants.models import Restaurant
from instamart.models import InstamartStore

def run():
    print("Updating Instamart Stores...")
    # Update all instamart stores
    instamart_stores = InstamartStore.objects.all()
    for store in instamart_stores:
        store.is_24hrs = False
        store.opening_time = time(5, 0)
        store.closing_time = time(23, 0)
        store.save()
    print(f"Updated {instamart_stores.count()} Instamart stores.")

    print("Updating Restaurants...")
    restaurants = Restaurant.objects.all()
    
    # Let's set some default hours for all
    for i, r in enumerate(restaurants):
        r.is_24hrs = False
        
        # Pick a few to be Midnight Restaurants (Open 7 PM to 4 AM)
        if i % 4 == 0:
            r.opening_time = time(19, 0)
            r.closing_time = time(4, 0)
        # Pick a few to be Early Closers (Open 8 AM to 3 PM)
        # Since it's ~3:30 PM now, these will be CLOSED, letting us test the UI!
        elif i % 5 == 0:
            r.opening_time = time(8, 0)
            r.closing_time = time(15, 0)
        # Regular Daytime Restaurants (Open 8 AM to 10 PM)
        else:
            r.opening_time = time(8, 0)
            r.closing_time = time(22, 0)
            
        r.save()
        
    print(f"Updated {restaurants.count()} Restaurants.")
    
if __name__ == '__main__':
    run()

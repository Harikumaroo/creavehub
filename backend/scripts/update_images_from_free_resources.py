"""
Script to update restaurant and menu item images from free image resources.

Supports:
- Unsplash API (requires API key)
- Pexels API (requires API key)
- Pixabay API (requires API key)
- Picsum.photos (no key needed)
"""

import os
import requests
from typing import Optional, List
from django.core.management.base import BaseCommand
from django.db import transaction

# Import your models
from restaurants.models import Restaurant
from menu.models import MenuItem


class ImageProvider:
    """Base class for image providers"""
    
    def get_image_url(self, query: str) -> Optional[str]:
        raise NotImplementedError


class PicsumPhotosProvider(ImageProvider):
    """Picsum.photos - Free placeholder images, no API key needed"""
    
    BASE_URL = "https://picsum.photos"
    
    def __init__(self):
        self.counter = 0
    
    def get_image_url(self, query: str) -> Optional[str]:
        """Returns a random image from picsum.photos"""
        # Use counter to get different images
        self.counter += 1
        # Picsum returns random images with seed parameter
        return f"{self.BASE_URL}/800/600?random={self.counter}"


class UnsplashProvider(ImageProvider):
    """Unsplash API - Requires UNSPLASH_API_KEY"""
    
    BASE_URL = "https://api.unsplash.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("UNSPLASH_API_KEY")
        if not self.api_key:
            raise ValueError("UNSPLASH_API_KEY environment variable not set")
    
    def get_image_url(self, query: str) -> Optional[str]:
        """Fetch image URL from Unsplash"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/search/photos",
                params={
                    "query": query,
                    "per_page": 1,
                    "client_id": self.api_key,
                },
                timeout=5
            )
            data = response.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
        except Exception as e:
            print(f"Error fetching from Unsplash: {e}")
        return None


class PexelsProvider(ImageProvider):
    """Pexels API - Requires PEXELS_API_KEY"""
    
    BASE_URL = "https://api.pexels.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            raise ValueError("PEXELS_API_KEY environment variable not set")
    
    def get_image_url(self, query: str) -> Optional[str]:
        """Fetch image URL from Pexels"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={"query": query, "per_page": 1},
                headers={"Authorization": self.api_key},
                timeout=5
            )
            data = response.json()
            if data.get("photos"):
                return data["photos"][0]["src"]["large"]
        except Exception as e:
            print(f"Error fetching from Pexels: {e}")
        return None


class PixabayProvider(ImageProvider):
    """Pixabay API - Requires PIXABAY_API_KEY"""
    
    BASE_URL = "https://pixabay.com/api/"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PIXABAY_API_KEY")
        if not self.api_key:
            raise ValueError("PIXABAY_API_KEY environment variable not set")
    
    def get_image_url(self, query: str) -> Optional[str]:
        """Fetch image URL from Pixabay"""
        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    "q": query,
                    "key": self.api_key,
                    "per_page": 1,
                    "image_type": "photo"
                },
                timeout=5
            )
            data = response.json()
            if data.get("hits"):
                return data["hits"][0]["largeImageURL"]
        except Exception as e:
            print(f"Error fetching from Pixabay: {e}")
        return None


class ImageUpdater:
    """Main class to update images in database"""
    
    # Keywords for different cuisine types
    CUISINE_KEYWORDS = {
        "pizza": ["pizza", "italian food"],
        "burger": ["burger", "fast food"],
        "sushi": ["sushi", "japanese food"],
        "chinese": ["chinese restaurant", "asian food"],
        "indian": ["indian food", "curry"],
        "mexican": ["mexican food", "tacos"],
        "thai": ["thai food", "noodles"],
        "american": ["american food", "steak"],
        "vegetarian": ["vegetarian food", "salad"],
        "seafood": ["seafood", "fish"],
        "dessert": ["dessert", "cake"],
        "breakfast": ["breakfast", "pancakes"],
    }
    
    def __init__(self, provider: ImageProvider = None, dry_run: bool = False):
        self.provider = provider or PicsumPhotosProvider()
        self.dry_run = dry_run
        self.stats = {
            "restaurants_updated": 0,
            "restaurants_skipped": 0,
            "menu_items_updated": 0,
            "menu_items_skipped": 0,
        }
    
    def get_cuisine_keyword(self, name: str) -> str:
        """Determine cuisine type from restaurant/item name"""
        name_lower = name.lower()
        
        for cuisine, keywords in self.CUISINE_KEYWORDS.items():
            if any(keyword in name_lower for keyword in keywords):
                return keywords[0]
        
        # Return generic keywords based on content
        if any(word in name_lower for word in ["restaurant", "cafe", "bistro"]):
            return "restaurant food"
        return "food"
    
    def update_restaurant_images(self):
        """Update all restaurant logos and cover images"""
        print("\n" + "="*60)
        print("UPDATING RESTAURANT IMAGES")
        print("="*60)
        
        restaurants = Restaurant.objects.filter(is_active=True)
        total = restaurants.count()
        
        for idx, restaurant in enumerate(restaurants, 1):
            print(f"\n[{idx}/{total}] Processing: {restaurant.name}")
            
            # Get cuisine type from name
            cuisine = self.get_cuisine_keyword(restaurant.name)
            
            try:
                # Update logo
                if not restaurant.logo or "loremflickr" in restaurant.logo:
                    logo_url = self.provider.get_image_url(f"{cuisine} logo")
                    if logo_url:
                        if not self.dry_run:
                            restaurant.logo = logo_url
                        print(f"  ✓ Logo: {logo_url[:60]}...")
                        self.stats["restaurants_updated"] += 1
                    else:
                        print(f"  ✗ Could not fetch logo image")
                        self.stats["restaurants_skipped"] += 1
                else:
                    print(f"  - Logo already set, skipping")
                    self.stats["restaurants_skipped"] += 1
                
                # Update cover image
                if not restaurant.cover_image or "loremflickr" in restaurant.cover_image:
                    cover_url = self.provider.get_image_url(cuisine)
                    if cover_url:
                        if not self.dry_run:
                            restaurant.cover_image = cover_url
                        print(f"  ✓ Cover: {cover_url[:60]}...")
                        self.stats["restaurants_updated"] += 1
                    else:
                        print(f"  ✗ Could not fetch cover image")
                        self.stats["restaurants_skipped"] += 1
                else:
                    print(f"  - Cover already set, skipping")
                    self.stats["restaurants_skipped"] += 1
                
                if not self.dry_run:
                    restaurant.save(update_fields=["logo", "cover_image"])
                    
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                self.stats["restaurants_skipped"] += 2
    
    def update_menu_item_images(self, restaurant_filter: Optional[str] = None):
        """Update all menu item images"""
        print("\n" + "="*60)
        print("UPDATING MENU ITEM IMAGES")
        print("="*60)
        
        query = MenuItem.objects.filter(is_available=True)
        
        if restaurant_filter:
            query = query.filter(restaurant__name__icontains=restaurant_filter)
        
        total = query.count()
        
        for idx, item in enumerate(query, 1):
            if idx % 50 == 0:
                print(f"Progress: {idx}/{total} items processed...")
            
            try:
                # Skip if image already exists and isn't placeholder
                if item.image and "loremflickr" not in item.image and "picsum" not in item.image:
                    continue
                
                # Get appropriate search query
                search_query = f"{item.name} food"
                image_url = self.provider.get_image_url(search_query)
                
                if image_url:
                    if not self.dry_run:
                        item.image = image_url
                        item.save(update_fields=["image"])
                    self.stats["menu_items_updated"] += 1
                else:
                    self.stats["menu_items_skipped"] += 1
                    
            except Exception as e:
                print(f"  ✗ Error updating {item.name}: {str(e)}")
                self.stats["menu_items_skipped"] += 1
    
    def print_stats(self):
        """Print update statistics"""
        print("\n" + "="*60)
        print("UPDATE STATISTICS")
        print("="*60)
        print(f"Restaurants Updated: {self.stats['restaurants_updated']}")
        print(f"Restaurants Skipped: {self.stats['restaurants_skipped']}")
        print(f"Menu Items Updated: {self.stats['menu_items_updated']}")
        print(f"Menu Items Skipped: {self.stats['menu_items_skipped']}")
        print("="*60)
    
    def run(self, update_restaurants: bool = True, update_items: bool = True,
            restaurant_filter: Optional[str] = None):
        """Run the complete update process"""
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be made")
        
        if update_restaurants:
            self.update_restaurant_images()
        
        if update_items:
            self.update_menu_item_images(restaurant_filter)
        
        self.print_stats()


def main():
    """Entry point for the script"""
    
    print("\n🖼️  CraveHub Image Update Tool")
    print("="*60)
    
    # Try to use a provider with API key if available
    provider = None
    
    if os.getenv("UNSPLASH_API_KEY"):
        print("✓ Using Unsplash API")
        provider = UnsplashProvider()
    elif os.getenv("PEXELS_API_KEY"):
        print("✓ Using Pexels API")
        provider = PexelsProvider()
    elif os.getenv("PIXABAY_API_KEY"):
        print("✓ Using Pixabay API")
        provider = PixabayProvider()
    else:
        print("⚠️  No API keys found, using Picsum.photos (free, no key needed)")
        provider = PicsumPhotosProvider()
    
    # Initialize updater
    updater = ImageUpdater(provider=provider, dry_run=False)
    
    # Run update
    with transaction.atomic():
        updater.run(update_restaurants=True, update_items=True)


if __name__ == "__main__":
    main()

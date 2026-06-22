"""
Test script to verify image update tools are working correctly.
"""

import os
import sys
import django
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cravehub.settings")
django.setup()

from restaurants.models import Restaurant
from menu.models import MenuItem
from scripts.update_images_from_free_resources import (
    ImageUpdater, PicsumPhotosProvider, 
    UnsplashProvider, PexelsProvider, PixabayProvider
)


def test_database():
    """Test database connectivity and data"""
    print("\n" + "="*60)
    print("🗄️  Database Test")
    print("="*60)
    
    restaurant_count = Restaurant.objects.count()
    menu_item_count = MenuItem.objects.count()
    
    print(f"✓ Restaurants: {restaurant_count}")
    print(f"✓ Menu Items: {menu_item_count}")
    
    if restaurant_count == 0:
        print("⚠️  No restaurants found!")
        return False
    
    # Show sample data
    restaurant = Restaurant.objects.first()
    print(f"\nSample Restaurant: {restaurant.name}")
    print(f"  - Logo: {restaurant.logo[:60] if restaurant.logo else 'None'}...")
    print(f"  - Cover: {restaurant.cover_image[:60] if restaurant.cover_image else 'None'}...")
    
    items = restaurant.menu_items.all()[:3]
    print(f"\nSample Menu Items ({len(items)}):")
    for item in items:
        print(f"  - {item.name}: {item.image[:60] if item.image else 'None'}...")
    
    return True


def test_provider(provider_class, name: str, api_key: str = None):
    """Test a specific provider"""
    print(f"\n🧪 Testing {name}...")
    
    try:
        if api_key:
            provider = provider_class(api_key=api_key)
        else:
            provider = provider_class()
        
        # Try to get an image
        url = provider.get_image_url("pizza food")
        
        if url:
            print(f"✓ {name} working! Got image: {url[:60]}...")
            return True
        else:
            print(f"⚠️  {name} returned no image")
            return False
            
    except Exception as e:
        print(f"✗ {name} error: {str(e)}")
        return False


def test_providers():
    """Test all available providers"""
    print("\n" + "="*60)
    print("🔌 Provider Tests")
    print("="*60)
    
    # Always test Picsum
    test_provider(PicsumPhotosProvider, "Picsum.photos")
    
    # Test API-based providers if keys are available
    if os.getenv("UNSPLASH_API_KEY"):
        test_provider(UnsplashProvider, "Unsplash", os.getenv("UNSPLASH_API_KEY"))
    
    if os.getenv("PEXELS_API_KEY"):
        test_provider(PexelsProvider, "Pexels", os.getenv("PEXELS_API_KEY"))
    
    if os.getenv("PIXABAY_API_KEY"):
        test_provider(PixabayProvider, "Pixabay", os.getenv("PIXABAY_API_KEY"))


def test_dry_run():
    """Test with dry run"""
    print("\n" + "="*60)
    print("🎯 Dry Run Test")
    print("="*60)
    
    try:
        provider = PicsumPhotosProvider()
        updater = ImageUpdater(provider=provider, dry_run=True)
        
        print("\nRunning dry-run update on 1 restaurant...")
        
        restaurants = Restaurant.objects.all()[:1]
        if restaurants:
            rest = restaurants[0]
            cuisine = updater.get_cuisine_keyword(rest.name)
            
            logo_url = provider.get_image_url(f"{cuisine} logo")
            cover_url = provider.get_image_url(cuisine)
            
            print(f"\nWould update: {rest.name}")
            print(f"  Logo: {logo_url[:60] if logo_url else 'FAILED'}...")
            print(f"  Cover: {cover_url[:60] if cover_url else 'FAILED'}...")
            
            if logo_url and cover_url:
                print("✓ Dry run successful!")
            else:
                print("⚠️  Some images failed to fetch")
        
    except Exception as e:
        print(f"✗ Dry run error: {str(e)}")


def show_recommendations():
    """Show recommendations based on test results"""
    print("\n" + "="*60)
    print("💡 Recommendations")
    print("="*60)
    
    if os.getenv("UNSPLASH_API_KEY"):
        print("✓ You have Unsplash API key - use: --provider unsplash")
    elif os.getenv("PEXELS_API_KEY"):
        print("✓ You have Pexels API key - use: --provider pexels")
    elif os.getenv("PIXABAY_API_KEY"):
        print("✓ You have Pixabay API key - use: --provider pixabay")
    else:
        print("⚠️  No API keys configured")
        print("   Picsum works without API key: --provider picsum")
    
    print("\n📖 Next steps:")
    print("1. Read IMAGE_UPDATE_GUIDE.md for detailed instructions")
    print("2. Run: python manage.py update_images --dry-run")
    print("3. If happy with preview, run: python manage.py update_images")


def main():
    print("\n" + "="*60)
    print("🖼️  CraveHub Image Update - Verification Test")
    print("="*60)
    
    # Test database
    if not test_database():
        print("\n✗ Database test failed!")
        return
    
    # Test providers
    test_providers()
    
    # Test dry run
    test_dry_run()
    
    # Show recommendations
    show_recommendations()
    
    print("\n✓ All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

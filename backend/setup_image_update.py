"""
Quick setup helper for image update tool.
Run this to set up API keys easily.
"""

import os
import sys
import subprocess
from pathlib import Path


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default"""
    if default:
        display = f"{prompt} [{default}]: "
    else:
        display = f"{prompt}: "
    
    value = input(display).strip()
    return value or default


def test_provider(provider_name: str, api_key: str = None) -> bool:
    """Test if a provider works"""
    print(f"\n🧪 Testing {provider_name}...")
    
    try:
        if provider_name == "picsum":
            import requests
            response = requests.get("https://picsum.photos/800/600", timeout=5)
            if response.status_code == 200:
                print(f"✓ {provider_name} is working!")
                return True
        else:
            print(f"⚠️  API key required. Please set {provider_name.upper()}_API_KEY")
            return False
    except Exception as e:
        print(f"✗ Error testing {provider_name}: {e}")
        return False


def setup_api_keys():
    """Interactive setup for API keys"""
    
    print("\n" + "="*60)
    print("🔑 CraveHub Image Update - API Key Setup")
    print("="*60)
    
    print("\n1️⃣  Unsplash (recommended for best quality)")
    print("   - Get free API key: https://unsplash.com/developers")
    unsplash_key = get_input("   Unsplash API Key (leave blank to skip)")
    
    print("\n2️⃣  Pexels (alternative option)")
    print("   - Get free API key: https://www.pexels.com/api/")
    pexels_key = get_input("   Pexels API Key (leave blank to skip)")
    
    print("\n3️⃣  Pixabay (another alternative)")
    print("   - Get free API key: https://pixabay.com/api/docs/")
    pixabay_key = get_input("   Pixabay API Key (leave blank to skip)")
    
    # Create .env file
    backend_path = Path(__file__).parent
    env_file = backend_path / ".env"
    
    if any([unsplash_key, pexels_key, pixabay_key]):
        with open(env_file, "w") as f:
            if unsplash_key:
                f.write(f"UNSPLASH_API_KEY={unsplash_key}\n")
            if pexels_key:
                f.write(f"PEXELS_API_KEY={pexels_key}\n")
            if pixabay_key:
                f.write(f"PIXABAY_API_KEY={pixabay_key}\n")
        
        print(f"\n✓ Created {env_file}")
    
    # Test providers
    print("\n" + "="*60)
    print("🧪 Testing Providers")
    print("="*60)
    
    test_provider("picsum")
    if unsplash_key:
        test_provider("unsplash", unsplash_key)
    if pexels_key:
        test_provider("pexels", pexels_key)
    if pixabay_key:
        test_provider("pixabay", pixabay_key)


def show_usage():
    """Show usage examples"""
    
    print("\n" + "="*60)
    print("📖 Usage Examples")
    print("="*60)
    
    examples = [
        ("Quick start (no API key needed)", "python manage.py update_images --provider picsum"),
        ("Preview changes", "python manage.py update_images --dry-run"),
        ("Update only restaurants", "python manage.py update_images --restaurants-only"),
        ("Update specific restaurant", 'python manage.py update_images --restaurant "Pizza Paradise"'),
        ("Use Unsplash API", "python manage.py update_images --provider unsplash"),
    ]
    
    for desc, cmd in examples:
        print(f"\n{desc}:")
        print(f"  > {cmd}")


def main():
    """Main setup flow"""
    
    print("\n🖼️  CraveHub Image Update Setup")
    print("="*60)
    
    choice = input("\nWhat would you like to do?\n"
                   "1. Setup API keys\n"
                   "2. Show usage examples\n"
                   "3. Exit\n"
                   "Choice [1-3]: ").strip()
    
    if choice == "1":
        setup_api_keys()
        print("\n✓ Setup complete!")
    elif choice == "2":
        show_usage()
    else:
        print("Goodbye!")
        return
    
    print("\n📖 For more details, see: IMAGE_UPDATE_GUIDE.md")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

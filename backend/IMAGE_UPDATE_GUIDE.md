# 🖼️ CraveHub Image Update Guide

This guide explains how to replace placeholder images with real, free images from professional image resources.

## 📋 Overview

You have:
- **26 Restaurants** needing logo + cover images
- **2,336 Menu Items** needing food images
- Currently using placeholder images from loremflickr

## 🆓 Free Image Resources

### 1. **Picsum.photos** (RECOMMENDED - No API key needed)
- **URL**: https://picsum.photos
- **Pros**: 
  - No authentication required
  - Fast and reliable
  - Professional stock photos
  - 10,000+ images available
- **Usage**: Works out of the box!

### 2. **Unsplash API** (Free with account)
- **URL**: https://unsplash.com/developers
- **Steps**:
  1. Go to https://unsplash.com/developers
  2. Create free account
  3. Create new app
  4. Get your API key
  5. Set environment variable: `UNSPLASH_API_KEY=your_key`

### 3. **Pexels API** (Free with account)
- **URL**: https://www.pexels.com/api/
- **Steps**:
  1. Go to https://www.pexels.com/api/
  2. Create account
  3. Get API key
  4. Set environment variable: `PEXELS_API_KEY=your_key`

### 4. **Pixabay API** (Free with account)
- **URL**: https://pixabay.com/api/docs/
- **Steps**:
  1. Go to https://pixabay.com/api/docs/
  2. Create free account
  3. Get API key
  4. Set environment variable: `PIXABAY_API_KEY=your_key`

## 🚀 Quick Start

### Option 1: Use Picsum.photos (Easiest)
```bash
cd backend
python manage.py update_images --provider picsum
```

### Option 2: Use Unsplash (Better quality)
```bash
# Set API key first (Windows PowerShell)
$env:UNSPLASH_API_KEY = "your_api_key_here"

# Then run
python manage.py update_images --provider unsplash
```

### Option 3: Use Pexels
```bash
$env:PEXELS_API_KEY = "your_api_key_here"
python manage.py update_images --provider pexels
```

### Option 4: Use Pixabay
```bash
$env:PIXABAY_API_KEY = "your_api_key_here"
python manage.py update_images --provider pixabay
```

## 📝 Usage Examples

### Preview changes (dry run) - No actual updates
```bash
python manage.py update_images --provider picsum --dry-run
```

### Update only restaurants
```bash
python manage.py update_images --restaurants-only
```

### Update only menu items
```bash
python manage.py update_images --items-only
```

### Update only for one restaurant
```bash
python manage.py update_images --restaurant "Pizza Paradise"
```

### Combine options
```bash
# Update only Pizza Paradise menu items
python manage.py update_images --items-only --restaurant "Pizza Paradise"

# Dry run with Unsplash
python manage.py update_images --provider unsplash --dry-run
```

## 🔧 Setting Environment Variables Permanently

### Windows (PowerShell)
Edit your profile:
```powershell
notepad $PROFILE
```
Add these lines:
```powershell
$env:UNSPLASH_API_KEY = "your_key"
$env:PEXELS_API_KEY = "your_key"
$env:PIXABAY_API_KEY = "your_key"
```

### Windows (Command Prompt)
```cmd
setx UNSPLASH_API_KEY "your_key"
setx PEXELS_API_KEY "your_key"
setx PIXABAY_API_KEY "your_key"
```

### Windows (.env file in backend folder)
Create `backend/.env`:
```
UNSPLASH_API_KEY=your_key_here
PEXELS_API_KEY=your_key_here
PIXABAY_API_KEY=your_key_here
```

Then load it in your Django settings or use python-dotenv package.

## 📊 What Gets Updated

### Restaurants
- **Logo**: Restaurant brand image
- **Cover Image**: Large banner image for restaurant page

### Menu Items
- **Image**: Food/dish image specific to each item

## 🎯 How It Works

1. **Analyzes names**: Reads restaurant/item names to determine food type
2. **Recognizes cuisine**: Detects "Pizza", "Burger", "Sushi", "Chinese", etc.
3. **Searches images**: Queries free APIs for appropriate images
4. **Updates database**: Replaces old image URLs with new ones
5. **Skips existing**: Doesn't update items that already have custom images

## 🚨 Important Notes

- **API Rate Limits**: 
  - Picsum: Unlimited (local service)
  - Unsplash: 50 requests/hour (free)
  - Pexels: 200 requests/hour (free)
  - Pixabay: 150 requests/day (free)

- **Processing Time**:
  - With Picsum: ~2-5 minutes for all items
  - With APIs: ~10-30 minutes (depends on rate limits)

- **Recommendations**:
  - Start with `--dry-run` to see what will change
  - Use `--restaurants-only` first, then `--items-only`
  - Use `--provider picsum` for fastest results

## ✅ Verification

After running the command, verify in Django admin:

1. Go to `http://localhost:8000/admin/restaurants/restaurant/`
2. Click any restaurant to see logo + cover image
3. Go to menu items and verify food images loaded

Or check via API:
```bash
curl http://localhost:8000/api/restaurants/
```

## 🔄 Batch Updates

For testing first, try updating just one restaurant:
```bash
# Test with Pizza Paradise
python manage.py update_images --restaurant "Pizza Paradise" --dry-run

# If happy with results, actually update it
python manage.py update_images --restaurant "Pizza Paradise"
```

## 🐛 Troubleshooting

### "API key not found" error
```bash
# Check if environment variable is set
echo $env:UNSPLASH_API_KEY  # PowerShell
echo %UNSPLASH_API_KEY%     # Command Prompt
```

### Slow updates
- Use Picsum (no API calls)
- Run with `--restaurants-only` first
- Try `--items-only --restaurant "Name"`

### Images not showing in frontend
- Check that image URLs are accessible (try in browser)
- Verify database update: `python manage.py shell`
- Clear browser cache

### Rate limit exceeded
- Wait and try again later
- Use a different provider
- Use `--provider picsum` (no rate limits)

## 📚 Python Script Usage

You can also use the Python script directly:

```python
from scripts.update_images_from_free_resources import ImageUpdater, UnsplashProvider

# Create updater with Unsplash
provider = UnsplashProvider(api_key="your_key")
updater = ImageUpdater(provider=provider, dry_run=False)

# Run update
updater.run(update_restaurants=True, update_items=True)

# Check stats
updater.print_stats()
```

## 🎨 Customization

To customize image search queries, edit [update_images_from_free_resources.py](update_images_from_free_resources.py):

```python
CUISINE_KEYWORDS = {
    "pizza": ["pizza", "italian food"],
    "burger": ["burger", "fast food"],
    # Add more here...
}
```

---

**Happy Updating! 🎉**

For questions or issues, check the logs or reach out to the development team.

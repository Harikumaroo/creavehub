# 🖼️ CraveHub Image Update - Quick Reference

## ⚡ Super Quick Start (No API Key Needed)

```bash
cd backend
python manage.py update_images --provider picsum
```

That's it! ✨

## 🎯 Common Commands

```bash
# Preview what will change (DRY RUN - no updates)
python manage.py update_images --dry-run

# Update restaurants only
python manage.py update_images --restaurants-only

# Update menu items only  
python manage.py update_images --items-only

# Update specific restaurant
python manage.py update_images --restaurant "Pizza Paradise"

# Use Unsplash (better quality, requires API key)
python manage.py update_images --provider unsplash

# Use Pexels
python manage.py update_images --provider pexels

# Use Pixabay
python manage.py update_images --provider pixabay
```

## 📊 What's Being Updated

| Target | Current | New |
|--------|---------|-----|
| 26 Restaurants | loremflickr placeholder | Professional images |
| 2,336 Menu Items | loremflickr placeholder | Food-specific images |

## 🔑 API Keys (Optional - Get Better Images)

### Unsplash
1. Visit: https://unsplash.com/developers
2. Create account → Create app → Copy API key
3. Set: `$env:UNSPLASH_API_KEY = "your_key"`

### Pexels
1. Visit: https://www.pexels.com/api/
2. Create account → Copy API key
3. Set: `$env:PEXELS_API_KEY = "your_key"`

### Pixabay
1. Visit: https://pixabay.com/api/docs/
2. Create account → Copy API key
3. Set: `$env:PIXABAY_API_KEY = "your_key"`

## 📁 Files Created

- `update_images_from_free_resources.py` - Main script
- `core/management/commands/update_images.py` - Django command
- `setup_image_update.py` - Interactive setup helper
- `test_image_update.py` - Verification tool
- `IMAGE_UPDATE_GUIDE.md` - Full documentation

## 🧪 Verify It Works

```bash
# Test setup
python test_image_update.py

# Interactive setup for API keys
python setup_image_update.py
```

## ✅ Best Practices

1. **Always do dry-run first**
   ```bash
   python manage.py update_images --dry-run
   ```

2. **Update restaurants first, then items**
   ```bash
   python manage.py update_images --restaurants-only
   python manage.py update_images --items-only
   ```

3. **Test with one restaurant first**
   ```bash
   python manage.py update_images --restaurant "Pizza Paradise" --dry-run
   ```

4. **Use Picsum for speed, Unsplash for quality**
   - Picsum: Fast, no API key needed
   - Unsplash: Better quality, requires free API key

## 🚀 Full Process

```bash
# 1. Test everything works
python test_image_update.py

# 2. Preview changes
python manage.py update_images --dry-run

# 3. Update restaurants (usually faster)
python manage.py update_images --restaurants-only

# 4. Update menu items (takes longer)
python manage.py update_images --items-only

# 5. Verify in browser
# Go to: http://localhost:8000/admin/restaurants/restaurant/
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "API key not found" | Set environment variable: `$env:UNSPLASH_API_KEY = "key"` |
| No images showing | Check URL in database, or try different provider |
| Very slow | Use Picsum (fastest) or update `--restaurants-only` first |
| Rate limit error | Wait and retry, or use different provider |

## 📚 More Info

- Full guide: `IMAGE_UPDATE_GUIDE.md`
- Django command help: `python manage.py update_images --help`

---

**Ready to update? Start with:**
```bash
python manage.py update_images --provider picsum
```

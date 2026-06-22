"""
Django management command to update images from free resources.

Usage:
    python manage.py update_images --provider unsplash --dry-run
    python manage.py update_images --provider pexels
    python manage.py update_images --restaurants-only
    python manage.py update_images --items-only
    python manage.py update_images --restaurant "Pizza Paradise"
"""

import sys
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Update restaurant and menu item images from free image resources"
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--provider",
            type=str,
            choices=["picsum", "unsplash", "pexels", "pixabay"],
            default="picsum",
            help="Image provider to use (default: picsum - no API key needed)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )
        parser.add_argument(
            "--restaurants-only",
            action="store_true",
            help="Only update restaurant images",
        )
        parser.add_argument(
            "--items-only",
            action="store_true",
            help="Only update menu item images",
        )
        parser.add_argument(
            "--restaurant",
            type=str,
            help="Only update items for a specific restaurant (by name)",
        )
    
    def handle(self, *args, **options):
        # Import here to ensure Django is fully initialized
        from scripts.update_images_from_free_resources import (
            ImageUpdater, PicsumPhotosProvider, UnsplashProvider,
            PexelsProvider, PixabayProvider
        )
        
        provider_name = options["provider"]
        dry_run = options["dry_run"]
        restaurants_only = options["restaurants_only"]
        items_only = options["items_only"]
        restaurant_filter = options.get("restaurant")
        
        # Both can't be True
        if restaurants_only and items_only:
            raise CommandError("Cannot use both --restaurants-only and --items-only")
        
        # Determine what to update
        update_restaurants = not items_only
        update_items = not restaurants_only
        
        self.stdout.write(self.style.SUCCESS("\n🖼️  CraveHub Image Update Tool"))
        self.stdout.write("=" * 60)
        
        # Initialize provider
        try:
            if provider_name == "unsplash":
                self.stdout.write("Using Unsplash API")
                provider = UnsplashProvider()
            elif provider_name == "pexels":
                self.stdout.write("Using Pexels API")
                provider = PexelsProvider()
            elif provider_name == "pixabay":
                self.stdout.write("Using Pixabay API")
                provider = PixabayProvider()
            else:
                self.stdout.write(self.style.WARNING(
                    "Using Picsum.photos (free, no API key needed)"
                ))
                provider = PicsumPhotosProvider()
        except ValueError as e:
            raise CommandError(f"Provider initialization failed: {str(e)}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  DRY RUN MODE - No changes will be made\n"
            ))
        
        # Initialize updater
        updater = ImageUpdater(provider=provider, dry_run=dry_run)
        
        # Run update
        try:
            with transaction.atomic():
                updater.run(
                    update_restaurants=update_restaurants,
                    update_items=update_items,
                    restaurant_filter=restaurant_filter,
                )
            
            self.stdout.write(self.style.SUCCESS("\n✓ Image update completed successfully!"))
            
        except Exception as e:
            raise CommandError(f"Error during image update: {str(e)}")

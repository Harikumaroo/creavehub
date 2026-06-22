"""
CraveHub — Core Admin
"""

from django.contrib import admin
from .models import AppSector


@admin.register(AppSector)
class AppSectorAdmin(admin.ModelAdmin):
    list_display = ["emoji", "name", "route", "display_order", "is_active"]
    list_filter = ["is_active"]
    list_editable = ["display_order", "is_active"]
    search_fields = ["name"]
    ordering = ["display_order"]

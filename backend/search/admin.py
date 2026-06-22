from django.contrib import admin
from .models import SearchHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display  = ["user", "query", "created_at"]
    search_fields = ["user__mobile_number", "query"]
    ordering      = ["-created_at"]
    list_per_page = 50
    readonly_fields = ["id", "created_at", "updated_at"]

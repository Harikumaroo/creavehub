from django.contrib import admin
from .models import Notification, PushToken


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ["user", "title", "notif_type", "is_read", "created_at"]
    list_filter   = ["notif_type", "is_read", "created_at"]
    search_fields = ["user__mobile_number", "title", "body"]
    readonly_fields = ["id", "metadata", "created_at", "updated_at"]
    list_editable = ["is_read"]
    ordering      = ["-created_at"]
    list_per_page = 50

    @admin.action(description="Mark selected as read")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
    actions = [mark_read]


@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display  = ["user", "platform", "is_active", "created_at"]
    list_filter   = ["platform", "is_active"]
    search_fields = ["user__mobile_number", "token"]
    readonly_fields = ["id", "created_at", "updated_at"]

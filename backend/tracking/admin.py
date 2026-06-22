from django.contrib import admin
from .models import DeliveryAgent, OrderTracking, LocationPing


@admin.register(DeliveryAgent)
class DeliveryAgentAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "phone", "vehicle_type", "vehicle_number", "status", "is_active"]
    list_filter   = ["status", "is_active", "vehicle_type"]
    search_fields = ["full_name", "phone", "vehicle_number"]
    list_editable = ["status", "is_active"]
    readonly_fields = ["id", "current_latitude", "current_longitude", "last_location_at", "created_at", "updated_at"]


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display  = ["order", "agent", "eta_minutes", "updated_at"]
    search_fields = ["order__id", "agent__full_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(LocationPing)
class LocationPingAdmin(admin.ModelAdmin):
    list_display  = ["tracking", "latitude", "longitude", "created_at"]
    readonly_fields = ["id", "created_at"]
    ordering      = ["-created_at"]
    list_per_page = 100

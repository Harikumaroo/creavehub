from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP, DeviceSession, UserAddress, UserSettings


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ["mobile_number", "full_name", "email", "account_type", "is_verified", "created_at"]
    list_filter     = ["account_type", "is_verified", "is_active"]
    search_fields   = ["mobile_number", "full_name", "email"]
    ordering        = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets       = (
        ("Identity",     {"fields": ("id", "mobile_number", "full_name", "email")}),
        ("Status",       {"fields": ("is_verified", "is_active", "account_type")}),
        ("Permissions",  {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps",   {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets   = (
        (None, {"fields": ("mobile_number", "full_name", "email", "password1", "password2")}),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display  = ["mobile_number", "purpose", "is_used", "is_verified", "attempts", "expires_at", "created_at"]
    list_filter   = ["purpose", "is_used", "is_verified"]
    search_fields = ["mobile_number"]
    readonly_fields = ["id", "otp_hash", "created_at"]


@admin.register(DeviceSession)
class DeviceSessionAdmin(admin.ModelAdmin):
    list_display  = [
        "user", "device_type", "device_name", "ip_address",
        "is_active", "is_trusted", "login_time", "last_active", "logout_reason"
    ]
    list_filter   = ["device_type", "is_active", "is_trusted"]
    search_fields = ["user__mobile_number", "device_id", "ip_address"]
    readonly_fields = ["id", "refresh_token_id", "login_time"]
    actions       = ["revoke_sessions"]

    @admin.action(description="Revoke selected sessions")
    def revoke_sessions(self, request, queryset):
        for session in queryset.filter(is_active=True):
            session.mark_inactive(reason="admin_revoke")
        self.message_user(request, f"{queryset.count()} session(s) revoked.")


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ["user", "label", "flat_no", "street", "city", "state", "pincode", "is_default"]
    list_filter = ["city", "state", "is_default"]
    search_fields = ["user__mobile_number", "street", "city"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ["user", "push_notifications", "dark_mode", "language"]
    list_filter = ["push_notifications", "dark_mode", "language"]
    search_fields = ["user__mobile_number"]
    readonly_fields = ["user"]
import re
from rest_framework import serializers
from .models import User, DeviceSession, UserAddress, UserSettings


# ═══════════════════════════════════════════════════════════════
# VALIDATORS
# ═══════════════════════════════════════════════════════════════

def validate_mobile_number(value: str) -> str:
    cleaned = value.strip().replace(" ", "").replace("-", "")
    if not re.match(r'^\+?[1-9]\d{9,14}$', cleaned):
        raise serializers.ValidationError("Enter a valid mobile number (10–15 digits).")
    return cleaned


# ═══════════════════════════════════════════════════════════════
# REGISTRATION SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class RegisterMobileSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)


class RegisterVerifyOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    otp           = serializers.CharField(min_length=6, max_length=6)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric.")
        return value


class RegisterCompleteSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    full_name     = serializers.CharField(max_length=150)
    email         = serializers.EmailField(required=False, allow_blank=True)
    device_id     = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_type   = serializers.ChoiceField(
                        choices=["mobile", "web", "tablet", "unknown"],
                        required=False, default="unknown"
                    )
    device_name   = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)

    def validate_full_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Full name must be at least 2 characters.")
        return value.strip()


# ═══════════════════════════════════════════════════════════════
# LOGIN SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class LoginMobileSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)


class LoginVerifyOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    otp           = serializers.CharField(min_length=6, max_length=6)
    device_id     = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_type   = serializers.ChoiceField(
                        choices=["mobile", "web", "tablet", "unknown"],
                        required=False, default="unknown"
                    )
    device_name   = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric.")
        return value


# ═══════════════════════════════════════════════════════════════
# LOGOUT SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class DeviceLogoutSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()


# ═══════════════════════════════════════════════════════════════
# PROFILE SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class UserProfileSerializer(serializers.ModelSerializer):
    active_device_count = serializers.IntegerField(read_only=True)

    class Meta:
        model  = User
        fields = [
            "id", "mobile_number", "full_name", "email", "avatar",
            "is_verified", "account_type",
            "active_device_count", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "mobile_number", "is_verified",
            "account_type", "created_at", "updated_at",
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["full_name", "email", "avatar"]

    def validate_email(self, value):
        user = self.instance
        if value and User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


# ═══════════════════════════════════════════════════════════════
# DEVICE SESSION SERIALIZER
# ═══════════════════════════════════════════════════════════════

class DeviceSessionSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()

    class Meta:
        model  = DeviceSession
        fields = [
            "id", "device_id", "device_type", "device_name",
            "ip_address", "login_time", "last_active",
            "is_active", "is_trusted", "is_current",
            "location_city", "location_country",
        ]

    def get_is_current(self, obj):
        """Mark the session that matches the current request's JTI."""
        request = self.context.get("request")
        if not request:
            return False
        try:
            auth_header = request.auth
            if auth_header and hasattr(auth_header, "payload"):
                return obj.refresh_token_id == auth_header.payload.get("jti", "")
        except Exception:
            pass
        return False


# ═══════════════════════════════════════════════════════════════
# TOKEN REFRESH SERIALIZER
# ═══════════════════════════════════════════════════════════════

class TokenRefreshWithDeviceSerializer(serializers.Serializer):
    refresh = serializers.CharField()


# ═══════════════════════════════════════════════════════════════
# SETTINGS & ADDRESS SERIALIZERS
# ═══════════════════════════════════════════════════════════════

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            "id", "label", "flat_no", "building_name", "street", "landmark",
            "city", "state", "pincode", "full_address", "latitude", "longitude",
            "is_default", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = [
            "push_notifications", "email_notifications",
            "sms_notifications", "whatsapp_notifications", "dark_mode", "language"
        ]
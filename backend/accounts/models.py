import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


# ═══════════════════════════════════════════════════════════════
# CUSTOM USER MANAGER
# ═══════════════════════════════════════════════════════════════
class UserManager(BaseUserManager):
    """Mobile number is the unique identifier — no username/password."""

    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError("Mobile number is required.")
        extra_fields.setdefault("is_active", True)
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


# ═══════════════════════════════════════════════════════════════
# CUSTOM USER MODEL
# ═══════════════════════════════════════════════════════════════
class User(AbstractUser):
    """
    CraveHub custom user model.
    Auth: mobile_number + OTP only. No username/password login.
    Future-ready: account_type supports delivery partners, restaurant owners.
    """

    username      = None  # Disabled

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mobile_number = models.CharField(max_length=15, unique=True, db_index=True)
    email         = models.EmailField(blank=True, null=True, unique=True)
    full_name     = models.CharField(max_length=150, blank=True)
    avatar        = models.ImageField(upload_to="avatars/", null=True, blank=True)
    is_verified   = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    account_type  = models.CharField(
        max_length=20,
        choices=[
            ("customer",         "Customer"),
            ("delivery_partner", "Delivery Partner"),
            ("restaurant_owner", "Restaurant Owner"),
            ("admin",            "Admin"),
        ],
        default="customer",
        db_index=True,
    )

    USERNAME_FIELD  = "mobile_number"
    REQUIRED_FIELDS = []
    objects         = UserManager()

    class Meta:
        db_table     = "ch_users"
        verbose_name = "User"
        ordering     = ["-created_at"]
        indexes      = [
            models.Index(fields=["mobile_number"]),
            models.Index(fields=["email"]),
            models.Index(fields=["account_type"]),
        ]

    def __str__(self):
        return f"{self.full_name or 'Unnamed'} ({self.mobile_number})"

    @property
    def active_device_count(self):
        return self.device_sessions.filter(is_active=True).count()


# ═══════════════════════════════════════════════════════════════
# OTP MODEL
# ═══════════════════════════════════════════════════════════════
class OTP(models.Model):
    PURPOSE_REGISTER = "register"
    PURPOSE_LOGIN    = "login"
    PURPOSE_RESET    = "reset"

    PURPOSE_CHOICES = [
        (PURPOSE_REGISTER, "Registration"),
        (PURPOSE_LOGIN,    "Login"),
        (PURPOSE_RESET,    "Password Reset"),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mobile_number = models.CharField(max_length=15, db_index=True)
    otp_hash      = models.CharField(max_length=255)
    purpose       = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    is_used       = models.BooleanField(default=False)
    is_verified   = models.BooleanField(default=False)
    attempts      = models.PositiveSmallIntegerField(default=0)
    max_attempts  = models.PositiveSmallIntegerField(default=5)
    created_at    = models.DateTimeField(auto_now_add=True)
    expires_at    = models.DateTimeField()

    class Meta:
        db_table = "ch_otps"
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["mobile_number", "purpose"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"OTP [{self.purpose}] -> {self.mobile_number}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_max_attempts_reached(self):
        return self.attempts >= self.max_attempts

    def increment_attempt(self):
        self.attempts += 1
        self.save(update_fields=["attempts"])


# ═══════════════════════════════════════════════════════════════
# DEVICE SESSION MODEL
# ═══════════════════════════════════════════════════════════════
class DeviceSession(models.Model):
    DEVICE_MOBILE  = "mobile"
    DEVICE_WEB     = "web"
    DEVICE_TABLET  = "tablet"
    DEVICE_UNKNOWN = "unknown"

    DEVICE_CHOICES = [
        (DEVICE_MOBILE,  "Mobile App"),
        (DEVICE_WEB,     "Web Browser"),
        (DEVICE_TABLET,  "Tablet"),
        (DEVICE_UNKNOWN, "Unknown"),
    ]

    LOGOUT_REASON_CHOICES = [
        ("user_logout",  "User Logout"),
        ("admin_revoke", "Admin Revoke"),
        ("token_expire", "Token Expired"),
        ("security",     "Security Revoke"),
        ("logout_all",   "Logout All Devices"),
    ]

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name="device_sessions")
    device_id        = models.CharField(max_length=255, db_index=True)
    device_type      = models.CharField(max_length=20, choices=DEVICE_CHOICES, default=DEVICE_UNKNOWN)
    device_name      = models.CharField(max_length=150, blank=True)
    user_agent       = models.TextField(blank=True)
    ip_address       = models.GenericIPAddressField(null=True, blank=True)
    login_time       = models.DateTimeField(auto_now_add=True)
    last_active      = models.DateTimeField(auto_now_add=True)
    is_active        = models.BooleanField(default=True, db_index=True)
    refresh_token_id = models.CharField(max_length=255, unique=True)

    # Future scalability
    is_trusted       = models.BooleanField(default=False)
    trusted_at       = models.DateTimeField(null=True, blank=True)
    location_city    = models.CharField(max_length=100, blank=True)
    location_country = models.CharField(max_length=100, blank=True)
    logout_time      = models.DateTimeField(null=True, blank=True)
    logout_reason    = models.CharField(max_length=30, blank=True, choices=LOGOUT_REASON_CHOICES)

    class Meta:
        db_table = "ch_device_sessions"
        ordering = ["-login_time"]
        indexes  = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["device_id"]),
            models.Index(fields=["refresh_token_id"]),
            models.Index(fields=["login_time"]),
        ]

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.user.mobile_number} | {self.device_type} | {status}"

    def mark_inactive(self, reason="user_logout"):
        self.is_active     = False
        self.logout_time   = timezone.now()
        self.logout_reason = reason
        self.save(update_fields=["is_active", "logout_time", "logout_reason"])

    def touch(self):
        self.last_active = timezone.now()
        self.save(update_fields=["last_active"])


# ═══════════════════════════════════════════════════════════════
# USER ADDRESS MODEL
# ═══════════════════════════════════════════════════════════════
class UserAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    
    label = models.CharField(max_length=20, default="Home")
    flat_no = models.CharField(max_length=255, default="")
    building_name = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    full_address = models.TextField(blank=True)
    
    latitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ch_user_addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.label} - {self.user.mobile_number}"

    def save(self, *args, **kwargs):
        if self.is_default:
            UserAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════
# USER SETTINGS MODEL
# ═══════════════════════════════════════════════════════════════
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings", primary_key=True)
    push_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    whatsapp_notifications = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default="en")

    class Meta:
        db_table = "ch_user_settings"

    def __str__(self):
        return f"Settings - {self.user.mobile_number}"
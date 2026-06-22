import hashlib
import random
import string
import uuid
from datetime import timedelta

from django.utils import timezone


# ═══════════════════════════════════════════════════════════════
# OTP UTILITIES
# ═══════════════════════════════════════════════════════════════

OTP_LENGTH      = 6
OTP_EXPIRY_MINS = 10


def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=OTP_LENGTH))


def hash_otp(otp: str) -> str:
    """SHA-256 hash the OTP before storing."""
    return hashlib.sha256(otp.encode()).hexdigest()


def get_otp_expiry() -> object:
    """Return OTP expiry datetime (now + OTP_EXPIRY_MINS)."""
    return timezone.now() + timedelta(minutes=OTP_EXPIRY_MINS)


def verify_otp_hash(plain_otp: str, stored_hash: str) -> bool:
    """Constant-time comparison of hashed OTP."""
    return hashlib.sha256(plain_otp.encode()).hexdigest() == stored_hash


# ═══════════════════════════════════════════════════════════════
# DEVICE UTILITIES
# ═══════════════════════════════════════════════════════════════

def generate_device_id() -> str:
    """Generate a unique device ID if client does not provide one."""
    return str(uuid.uuid4())


def get_client_ip(request) -> str:
    """Extract real IP from request headers (proxy-aware)."""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def get_device_type(user_agent: str) -> str:
    """Infer device type from User-Agent string."""
    ua = user_agent.lower()
    if any(k in ua for k in ["iphone", "android", "mobile"]):
        return "mobile"
    if any(k in ua for k in ["ipad", "tablet"]):
        return "tablet"
    if any(k in ua for k in ["mozilla", "chrome", "safari", "firefox", "edge"]):
        return "web"
    return "unknown"


def get_user_agent(request) -> str:
    return request.META.get("HTTP_USER_AGENT", "")


# ═══════════════════════════════════════════════════════════════
# RESPONSE UTILITIES
# ═══════════════════════════════════════════════════════════════

def success_response(message: str, data: dict = None, status: int = 200) -> dict:
    return {
        "success": True,
        "message": message,
        "data":    data or {},
    }


def error_response(message: str, errors: dict = None, status: int = 400) -> dict:
    resp = {
        "success": False,
        "message": message,
    }
    if errors:
        resp["errors"] = errors
    return resp


# ═══════════════════════════════════════════════════════════════
# MOBILE NUMBER UTILITIES
# ═══════════════════════════════════════════════════════════════

def normalize_mobile(mobile: str) -> str:
    """Strip spaces and ensure E.164-ish format."""
    mobile = mobile.strip().replace(" ", "").replace("-", "")
    if not mobile.startswith("+"):
        mobile = "+91" + mobile.lstrip("0")   # Default: India
    return mobile
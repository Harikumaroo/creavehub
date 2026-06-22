"""
Service layer — all business logic lives here.
Views stay thin; services stay testable.
"""
import uuid
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from .models import User, OTP, DeviceSession
import logging
import os
from django.conf import settings as dj_settings

logger = logging.getLogger(__name__)
from .utils import (
    generate_otp, hash_otp, get_otp_expiry,
    verify_otp_hash, generate_device_id,
)
import re
from django.core.mail import EmailMessage


# ═══════════════════════════════════════════════════════════════
# OTP SERVICE
# ═══════════════════════════════════════════════════════════════

class OTPService:

    @staticmethod
    def send_otp(mobile_number: str, purpose: str) -> dict:
        """
        Generate + store OTP.
        Invalidate any previous unused OTPs for same mobile + purpose.
        Returns plain OTP (to be sent via SMS gateway).
        """
        # Invalidate old OTPs
        OTP.objects.filter(
            mobile_number=mobile_number,
            purpose=purpose,
            is_used=False,
        ).update(is_used=True)

        plain_otp  = generate_otp()
        otp_record = OTP.objects.create(
            mobile_number=mobile_number,
            otp_hash=hash_otp(plain_otp),
            purpose=purpose,
            expires_at=get_otp_expiry(),
        )

        # ── SMS Gateway Hook ──────────────────────────────────
        sms_backend = getattr(dj_settings, "SMS_BACKEND", "console")

        if sms_backend == "console":
            logger.info(f"DEVELOPMENT MODE (Console): OTP for {mobile_number} is {plain_otp}")
            return {"otp_id": str(otp_record.id)}

        # ── Twilio SMS Gateway ────────────────────────────────
        twilio_sid = getattr(dj_settings, "TWILIO_ACCOUNT_SID", "")
        twilio_token = getattr(dj_settings, "TWILIO_AUTH_TOKEN", "")
        twilio_from = getattr(dj_settings, "TWILIO_FROM_NUMBER", "")
        twilio_messaging_service_sid = getattr(dj_settings, "TWILIO_MESSAGING_SERVICE_SID", "")

        if sms_backend == "twilio" and twilio_sid and twilio_token and (twilio_from or twilio_messaging_service_sid):
            try:
                from twilio.rest import Client
                client = Client(twilio_sid, twilio_token)
                
                msg_kwargs = {
                    "body": f"Your CraveHub OTP is {plain_otp}. It is valid for {dj_settings.OTP_EXPIRY_MINUTES} minutes.",
                    "to": mobile_number
                }
                
                if twilio_messaging_service_sid:
                    msg_kwargs["messaging_service_sid"] = twilio_messaging_service_sid
                else:
                    msg_kwargs["from_"] = twilio_from
                    
                message = client.messages.create(**msg_kwargs)
                logger.info(f"OTP sent to {mobile_number} via Twilio, SID: {message.sid}")
            except Exception as e:
                logger.error(f"Failed to send OTP via Twilio: {e}")
                if getattr(dj_settings, "DEBUG", False):
                    logger.info(f"FALLBACK DEVELOPMENT MODE: OTP for {mobile_number} is {plain_otp}")
        else:
            logger.warning("Twilio credentials not configured or SMS_BACKEND != twilio. OTP not sent to mobile.")
            if getattr(dj_settings, "DEBUG", False):
                logger.info(f"DEVELOPMENT MODE: OTP for {mobile_number} is {plain_otp}")
        # ─────────────────────────────────────────────────────

        return {"otp_id": str(otp_record.id)}

    @staticmethod
    def verify_otp(mobile_number: str, plain_otp: str, purpose: str) -> tuple:
        """
        Validate OTP.
        Returns (success: bool, message: str, otp_record | None)
        """
        try:
            otp = OTP.objects.filter(
                mobile_number=mobile_number,
                purpose=purpose,
                is_used=False,
                is_verified=False,
            ).latest("created_at")
        except OTP.DoesNotExist:
            return False, "No active OTP found. Please request a new one.", None

        if otp.is_expired:
            return False, "OTP has expired. Please request a new one.", None

        if otp.is_max_attempts_reached:
            return False, "Maximum OTP attempts reached. Please request a new one.", None

        otp.increment_attempt()

        if not verify_otp_hash(plain_otp, otp.otp_hash):
            remaining = otp.max_attempts - otp.attempts
            return False, f"Invalid OTP. {remaining} attempt(s) remaining.", None

        otp.is_verified = True
        otp.save(update_fields=["is_verified"])
        return True, "OTP verified successfully.", otp

    @staticmethod
    def mark_otp_used(otp: OTP):
        otp.is_used = True
        otp.save(update_fields=["is_used"])


# ═══════════════════════════════════════════════════════════════
# JWT TOKEN SERVICE
# ═══════════════════════════════════════════════════════════════

class TokenService:

    @staticmethod
    def generate_tokens(user: User) -> dict:
        """Generate JWT access + refresh token pair."""
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        # Align access token JTI with the refresh token JTI so we can revoke
        # access tokens when the refresh token is blacklisted on logout.
        try:
            access["jti"] = refresh["jti"]
        except Exception:
            # graceful fallback
            pass
        return {
            "access_token":  str(access),
            "refresh_token": str(refresh),
            "jti":           str(refresh["jti"]),
        }

    @staticmethod
    def blacklist_token(refresh_token_str: str) -> bool:
        """Blacklist a refresh token (logout)."""
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
            return True
        except Exception:
            return False

    @staticmethod
    def blacklist_by_jti(jti: str) -> bool:
        """Blacklist a token by its JTI (for device-specific logout)."""
        try:
            outstanding = OutstandingToken.objects.get(jti=jti)
            BlacklistedToken.objects.get_or_create(token=outstanding)
            return True
        except OutstandingToken.DoesNotExist:
            return False


# ═══════════════════════════════════════════════════════════════
# REGISTRATION SERVICE
# ═══════════════════════════════════════════════════════════════

class RegistrationService:

    @staticmethod
    def initiate(mobile_number: str) -> tuple:
        """Step 1: Check if mobile is new, send OTP."""
        if User.objects.filter(mobile_number=mobile_number).exists():
            return False, "Mobile number already registered.", {}

        result = OTPService.send_otp(mobile_number, OTP.PURPOSE_REGISTER)
        return True, "OTP sent successfully.", result

    @staticmethod
    def verify_otp(mobile_number: str, plain_otp: str) -> tuple:
        """Step 2: Verify registration OTP."""
        success, message, otp = OTPService.verify_otp(
            mobile_number, plain_otp, OTP.PURPOSE_REGISTER
        )
        return success, message, {}

    @staticmethod
    @transaction.atomic
    def complete(mobile_number: str, full_name: str, email: str,
                 device_id: str, device_type: str, device_name: str,
                 ip_address: str, user_agent: str) -> tuple:
        """
        Step 3: Create user account + device session + return tokens.
        """
        # Confirm OTP was verified
        otp = OTP.objects.filter(
            mobile_number=mobile_number,
            purpose=OTP.PURPOSE_REGISTER,
            is_verified=True,
            is_used=False,
        ).last()
        if not otp:
            return False, "OTP not verified. Please complete OTP verification first.", {}

        if User.objects.filter(mobile_number=mobile_number).exists():
            return False, "Mobile number already registered.", {}

        user = User.objects.create_user(
            mobile_number=mobile_number,
            full_name=full_name,
            email=email or None,
            is_verified=True,
        )
        OTPService.mark_otp_used(otp)

        # Ensure settings are created
        from accounts.models import UserSettings
        UserSettings.objects.get_or_create(user=user)

        # Trigger welcome email
        from notifications.services import NotificationService
        NotificationService.send_email(
            user=user,
            subject="Welcome to CraveHub!",
            body=f"Hi {full_name},\n\nWelcome to CraveHub! We're excited to have you onboard. Get ready to satisfy your cravings.\n\nBest,\nThe CraveHub Team"
        )

        tokens  = TokenService.generate_tokens(user)
        session = DeviceSessionService.create_session(
            user=user,
            device_id=device_id or generate_device_id(),
            device_type=device_type,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            refresh_token_id=tokens["jti"],
        )

        return True, "Registration successful.", {
            "access_token":  tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "device_id":     str(session.id),
            "user":          _user_data(user),
        }


# ═══════════════════════════════════════════════════════════════
# LOGIN SERVICE
# ═══════════════════════════════════════════════════════════════

class LoginService:

    @staticmethod
    def initiate(mobile_number: str) -> tuple:
        """Step 1: Check user exists, send login OTP."""
        try:
            User.objects.get(mobile_number=mobile_number)
        except User.DoesNotExist:
            return False, "User not registered. Please create an account.", {}

        result = OTPService.send_otp(mobile_number, OTP.PURPOSE_LOGIN)
        return True, "OTP sent successfully.", result

    @staticmethod
    @transaction.atomic
    def verify_otp(mobile_number: str, plain_otp: str,
                   device_id: str, device_type: str, device_name: str,
                   ip_address: str, user_agent: str) -> tuple:
        """
        Step 2: Verify OTP → create device session → return tokens.
        Previous device sessions are NEVER invalidated.
        """
        success, message, otp = OTPService.verify_otp(
            mobile_number, plain_otp, OTP.PURPOSE_LOGIN
        )
        if not success:
            return False, message, {}

        user = User.objects.get(mobile_number=mobile_number)
        OTPService.mark_otp_used(otp)

        tokens  = TokenService.generate_tokens(user)
        session = DeviceSessionService.create_session(
            user=user,
            device_id=device_id or generate_device_id(),
            device_type=device_type,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            refresh_token_id=tokens["jti"],
        )

        return True, "Login successful.", {
            "access_token":  tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "device_id":     str(session.id),
            "user":          _user_data(user),
        }


# ═══════════════════════════════════════════════════════════════
# DEVICE SESSION SERVICE
# ═══════════════════════════════════════════════════════════════

class DeviceSessionService:

    @staticmethod
    def create_session(user, device_id, device_type, device_name,
                       ip_address, user_agent, refresh_token_id) -> DeviceSession:
        """
        Create a new device session.
        If the same device_id already has an active session, deactivate it first
        (user re-logged in on same device with new OTP).
        """
        DeviceSession.objects.filter(
            user=user,
            device_id=device_id,
            is_active=True,
        ).update(
            is_active=False,
            logout_time=timezone.now(),
            logout_reason="user_logout",
        )

        return DeviceSession.objects.create(
            user=user,
            device_id=device_id,
            device_type=device_type or DeviceSession.DEVICE_UNKNOWN,
            device_name=device_name or "",
            user_agent=user_agent or "",
            ip_address=ip_address or None,
            refresh_token_id=refresh_token_id,
        )

    @staticmethod
    def get_active_sessions(user) -> list:
        return DeviceSession.objects.filter(user=user, is_active=True).order_by("-login_time")

    @staticmethod
    def logout_device(user, session_id: str) -> tuple:
        """Revoke a specific device session."""
        try:
            session = DeviceSession.objects.get(
                id=session_id, user=user, is_active=True
            )
        except DeviceSession.DoesNotExist:
            return False, "Device session not found or already inactive."

        TokenService.blacklist_by_jti(session.refresh_token_id)
        session.mark_inactive(reason="user_logout")
        return True, "Device logged out successfully."

    @staticmethod
    def logout_all_devices(user) -> tuple:
        """Revoke all active sessions for a user."""
        sessions = DeviceSession.objects.filter(user=user, is_active=True)
        for session in sessions:
            TokenService.blacklist_by_jti(session.refresh_token_id)
            session.mark_inactive(reason="logout_all")
        return True, f"Logged out from {sessions.count()} device(s)."

    @staticmethod
    def update_last_active(refresh_token_id: str):
        """Called on every authenticated request."""
        DeviceSession.objects.filter(
            refresh_token_id=refresh_token_id, is_active=True
        ).update(last_active=timezone.now())


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _user_data(user: User) -> dict:
    return {
        "id":           str(user.id),
        "mobile_number": user.mobile_number,
        "full_name":    user.full_name,
        "email":        user.email,
        "is_verified":  user.is_verified,
        "account_type": user.account_type,
        "created_at":   user.created_at.isoformat(),
    }
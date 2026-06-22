"""
Django signals for CraveHub accounts.
Future hooks: audit logs, analytics, notifications.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch          import receiver
from .models import User, DeviceSession
import logging
from django.conf import settings as dj_settings

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if created:
        # Future: trigger welcome SMS, create cart, create wallet, etc.
        if getattr(dj_settings, "DEBUG", False):
            logger.debug("[SIGNAL] New user created: %s", instance.mobile_number)


@receiver(post_save, sender=DeviceSession)
def on_device_session_created(sender, instance, created, **kwargs):
    if created:
        # Future: send new device login alert SMS/push notification
        if getattr(dj_settings, "DEBUG", False):
            logger.debug(
                "[SIGNAL] New device session: %s for %s",
                instance.device_type, instance.user.mobile_number,
            )


@receiver(post_save, sender=DeviceSession)
def on_device_session_deactivated(sender, instance, created, **kwargs):
    if not created and not instance.is_active:
        # Future: log to audit trail, trigger security alert if reason=security
        if getattr(dj_settings, "DEBUG", False):
            logger.debug(
                "[SIGNAL] Session deactivated [%s]: %s",
                instance.logout_reason, instance.user.mobile_number,
            )
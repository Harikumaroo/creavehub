"""
CraveHub — Notification Signals
Auto-fires notifications when order status changes.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


def connect_signals():
    """Called from apps.py ready() to avoid circular imports."""
    from orders.models import OrderStatusHistory
    from .services import NotificationService

    @receiver(post_save, sender=OrderStatusHistory)
    def on_order_status_change(sender, instance, created, **kwargs):
        if not created:
            return
        try:
            NotificationService.send_order_notification(
                order=instance.order,
                notif_type=instance.status,
            )
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                "Notification signal failed: %s", exc
            )

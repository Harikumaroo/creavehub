"""
CraveHub — Notifications Service Layer
Handles creation, delivery, and push dispatch.
"""

from __future__ import annotations
import logging
from django.db import transaction
from .models import Notification, PushToken
from accounts.models import UserSettings

logger = logging.getLogger(__name__)


class NotificationService:

    # ── Creation ─────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def send(
        user,
        title: str,
        body: str,
        notif_type: str = Notification.NotificationType.SYSTEM,
        metadata: dict | None = None,
    ) -> Notification:
        """Create an in-app notification and attempt push delivery."""
        notif = Notification.objects.create(
            user=user,
            title=title,
            body=body,
            notif_type=notif_type,
            metadata=metadata or {},
        )
        NotificationService._dispatch_push(user, title, body, metadata or {})
        return notif

    @staticmethod
    def send_order_notification(order, notif_type: str) -> None:
        """Convenience method triggered by order status changes."""
        status_to_notif = {
            "pending":          Notification.NotificationType.ORDER_PLACED,
            "confirmed":        Notification.NotificationType.ORDER_CONFIRMED,
            "preparing":        Notification.NotificationType.ORDER_PREPARING,
            "out_for_delivery": Notification.NotificationType.ORDER_OUT_DELIVERY,
            "delivered":        Notification.NotificationType.ORDER_DELIVERED,
            "cancelled":        Notification.NotificationType.ORDER_CANCELLED,
        }
        
        mapped_type = status_to_notif.get(notif_type, Notification.NotificationType.SYSTEM)

        messages = {
            Notification.NotificationType.ORDER_PLACED:        ("Order Placed 🎉",        f"Your order #{str(order.id)[:8].upper()} has been placed successfully!"),
            Notification.NotificationType.ORDER_CONFIRMED:     ("Order Confirmed ✅",      f"Restaurant confirmed your order #{str(order.id)[:8].upper()}."),
            Notification.NotificationType.ORDER_PREPARING:     ("Preparing your food 🍳",  "Your order is being prepared. Hang tight!"),
            Notification.NotificationType.ORDER_OUT_DELIVERY:  ("Out for Delivery 🛵",     "Your order is on the way!"),
            Notification.NotificationType.ORDER_DELIVERED:     ("Order Received 🎉",       "Your order has been delivered. Enjoy your meal!"),
            Notification.NotificationType.ORDER_CANCELLED:     ("Order Cancelled ❌",      f"Order #{str(order.id)[:8].upper()} has been cancelled."),
        }
        title, body = messages.get(mapped_type, ("Update", "Your order status changed."))
        
        NotificationService.send(
            user=order.user,
            title=title,
            body=body,
            notif_type=mapped_type,
            metadata={"order_id": str(order.id)},
        )
        NotificationService.send_sms(order.user, f"{title} - {body}")
        NotificationService.send_whatsapp(order.user, f"[{title}] {body}")

        if mapped_type == Notification.NotificationType.ORDER_DELIVERED and order.user.email:
            html_bill = NotificationService._generate_bill_html(order)
            text_bill = f"Thank you for your order!\n\nOrder #{str(order.id)[:8].upper()}\nTotal: ₹{order.grand_total}\nStatus: Delivered"
            NotificationService.send_email(
                user=order.user,
                subject=f"Your CraveHub Bill - Order #{str(order.id)[:8].upper()}",
                body=text_bill,
                html_body=html_bill
            )

    @staticmethod
    def _generate_bill_html(order) -> str:
        items_html = ""
        for item in order.items.all():
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item.name} x {item.quantity}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">₹{item.line_total}</td>
            </tr>
            """
        
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <div style="background-color: #FC8019; padding: 20px; text-align: center; color: white;">
                <h2 style="margin: 0;">CraveHub</h2>
                <p style="margin: 5px 0 0;">Order Delivered Successfully!</p>
            </div>
            <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
                <h3 style="margin-top: 0;">Order #{str(order.id)[:8].upper()}</h3>
                <p style="margin: 4px 0;"><strong>Restaurant:</strong> {order.restaurant.name}</p>
                <p style="margin: 4px 0;"><strong>Date:</strong> {order.created_at.strftime('%B %d, %Y %I:%M %p')}</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr>
                            <th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Item</th>
                            <th style="text-align: right; padding: 8px; border-bottom: 2px solid #ddd;">Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <div style="margin-top: 20px; border-top: 2px solid #ddd; padding-top: 10px;">
                    <div style="padding: 4px 0; overflow: hidden;">
                        <span style="float: left;">Subtotal:</span>
                        <span style="float: right;">₹{order.subtotal}</span>
                    </div>
                    <div style="padding: 4px 0; overflow: hidden;">
                        <span style="float: left;">Delivery Fee:</span>
                        <span style="float: right;">₹{order.delivery_fee}</span>
                    </div>
                    <div style="padding: 4px 0; overflow: hidden;">
                        <span style="float: left;">Tax:</span>
                        <span style="float: right;">₹{order.tax}</span>
                    </div>
                    <div style="padding: 4px 0; overflow: hidden; color: green;">
                        <span style="float: left;">Discount:</span>
                        <span style="float: right;">-₹{order.discount}</span>
                    </div>
                    <div style="padding: 8px 0; overflow: hidden; font-weight: bold; font-size: 18px; border-top: 1px solid #eee; margin-top: 8px;">
                        <span style="float: left;">Grand Total:</span>
                        <span style="float: right;">₹{order.grand_total}</span>
                    </div>
                </div>
                
                <div style="margin-top: 30px; text-align: center; color: #777; font-size: 12px;">
                    <p>Thank you for ordering with CraveHub!</p>
                </div>
            </div>
        </div>
        """
        return html

    # ── Queries ───────────────────────────────────────────────

    @staticmethod
    def get_user_notifications(user, params) -> tuple:
        qs = (
            Notification.objects
            .filter(user=user)
            .order_by("-created_at")
        )
        total  = qs.count()
        sliced = qs[params.offset: params.offset + params.limit]
        return sliced, total

    @staticmethod
    def get_unread_count(user) -> int:
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    @transaction.atomic
    def mark_read(user, notification_ids: list) -> int:
        updated = Notification.objects.filter(
            user=user, id__in=notification_ids
        ).update(is_read=True)
        return updated

    @staticmethod
    @transaction.atomic
    def mark_all_read(user) -> int:
        return Notification.objects.filter(
            user=user, is_read=False
        ).update(is_read=True)

    # ── Push Token Management ─────────────────────────────────

    @staticmethod
    def register_push_token(user, token: str, platform: str) -> PushToken:
        obj, _ = PushToken.objects.update_or_create(
            token=token,
            defaults={"user": user, "platform": platform, "is_active": True},
        )
        return obj

    @staticmethod
    def _dispatch_push(user, title: str, body: str, data: dict) -> None:
        """
        FCM push dispatch stub.
        Replace with actual firebase-admin SDK call in production:
            from firebase_admin import messaging
            messaging.send(messaging.Message(...))
        """
        tokens = PushToken.objects.filter(
            user=user, is_active=True
        ).values_list("token", flat=True)

        if not tokens:
            return

        logger.info(
            "[PUSH] To: %s | Tokens: %d | Title: %s",
            user, len(tokens), title,
        )
        # TODO: integrate firebase-admin here

    # ── Simulated Dispatches (Email, SMS, WhatsApp) ─────────

    @staticmethod
    def send_email(user, subject: str, body: str, html_body: str = None) -> None:
        try:
            settings = user.settings
            if not settings.email_notifications:
                return
        except Exception:
            return

        if not user.email:
            return

        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings as dj_settings

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=dj_settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            if html_body:
                email.attach_alternative(html_body, "text/html")
            
            email.send(fail_silently=True)
            logger.info(f"Email sent to {user.email}: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {e}")

    @staticmethod
    def send_sms(user, message: str) -> None:
        try:
            settings = user.settings
            if not settings.sms_notifications:
                return
        except Exception:
            return

        # print("\n" + "="*50)
        # print(f"📱 [SIMULATED SMS] To: {user.mobile_number}")
        # print(f"Message: {message}")
        # print("="*50 + "\n")

    @staticmethod
    def send_whatsapp(user, message: str) -> None:
        try:
            settings = user.settings
            if not settings.whatsapp_notifications:
                return
        except Exception:
            return

        # print("\n" + "="*50)
        # print(f"💬 [SIMULATED WHATSAPP] To: {user.mobile_number}")
        # print(f"Message: {message}")
        # print("="*50 + "\n")

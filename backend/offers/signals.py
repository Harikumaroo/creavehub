from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Offer
from notifications.models import Notification
from accounts.models import User

@receiver(post_save, sender=Offer)
def notify_new_offer(sender, instance, created, **kwargs):
    if created and instance.is_active:
        title = "New Offer Unlocked! 🏷️"
        body = f"Use code {instance.coupon_code} to get a discount on your next order!"
        
        from notifications.services import NotificationService
        
        users = User.objects.select_related('settings').all()
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title=title,
                    body=body,
                    notif_type=Notification.NotificationType.OFFER_ALERT,
                    metadata={"offer_id": str(instance.id), "code": instance.coupon_code}
                )
            )
            try:
                # Trigger email if enabled
                if hasattr(user, 'settings') and user.settings.email_notifications:
                    NotificationService.send_email(
                        user=user, 
                        subject=title, 
                        body=body
                    )
            except Exception:
                pass
                
        Notification.objects.bulk_create(notifications, batch_size=100)

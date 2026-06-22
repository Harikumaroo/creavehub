from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Restaurant
from menu.models import MenuItem
from notifications.models import Notification
from accounts.models import User

@receiver(post_save, sender=Restaurant)
def notify_new_restaurant(sender, instance, created, **kwargs):
    if created:
        title = "New Restaurant Alert! 🍽️"
        body = f"{instance.name} is now open on CraveHub. Check out their menu!"
        
        # Broadcast to all users
        users = User.objects.all()
        notifications = [
            Notification(
                user=user,
                title=title,
                body=body,
                notif_type=Notification.NotificationType.SYSTEM,
                metadata={"restaurant_id": str(instance.id)}
            )
            for user in users
        ]
        Notification.objects.bulk_create(notifications, batch_size=100)

@receiver(post_save, sender=MenuItem)
def notify_new_menu_item(sender, instance, created, **kwargs):
    if created:
        title = f"New Dish at {instance.restaurant.name}! 🍲"
        body = f"Try the new {instance.name} for just ₹{instance.price}!"
        
        users = User.objects.all()
        notifications = [
            Notification(
                user=user,
                title=title,
                body=body,
                notif_type=Notification.NotificationType.SYSTEM,
                metadata={"restaurant_id": str(instance.restaurant.id), "menu_item_id": str(instance.id)}
            )
            for user in users
        ]
        Notification.objects.bulk_create(notifications, batch_size=100)

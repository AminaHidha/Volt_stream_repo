from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from users.models import User


@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    """
    Fires automatically AFTER a new user is saved to database.

    sender   → the model that sent the signal (User)
    instance → the actual user object that was just saved
    created  → True if new user, False if existing user was updated
    """

    # Only run when a NEW user is created, not when updated
    if created:
        Notification.objects.create(
            user=instance,
            title="Welcome to VoltStream! ⚡",
            message=f"Hi {instance.full_name}, welcome to VoltStream! "
            f"Start exploring EV charging stations near you.",
        )

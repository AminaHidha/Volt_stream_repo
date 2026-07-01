from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User


class Notification(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Self Foreign Key — allows notifications to thread/reply to each other
    # For example: "Booking Confirmed" → "Your charger is ready" (a follow-up)
    # null=True, blank=True means it's optional — top-level notifications have no parent
    parent = models.ForeignKey(
        'self',                          # 'self' means this same model
        on_delete=models.SET_NULL,       # if parent is deleted, child stays (parent becomes null)
        null=True,
        blank=True,
        related_name='replies'           # notification.replies.all() gives all replies to it
    )

    def __str__(self):
        return self.title


@receiver(post_save, sender=Notification)
def send_push_notification(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        fcm_token = getattr(instance.user, "fcm_token", None)

        if not fcm_token:
            print(f"No FCM token for user {instance.user.id}, skipping push")
            return

        from .sqs import send_notification_to_sqs

        send_notification_to_sqs(
            fcm_token=fcm_token,
            title=instance.title,
            body=instance.message,
            url="/notifications",
        )

    except Exception as e:
        print(f"Push notification error: {str(e)}")
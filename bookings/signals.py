from django.db.models.signals import post_save
from django.dispatch import receiver

from bookings.models import Booking
from notifications.models import Notification


@receiver(post_save, sender=Booking)
def booking_notification(sender, instance, created, **kwargs):
    """
    Fires automatically AFTER a booking is saved to database.

    Handles two cases:
    1. New booking created → send confirmation notification
    2. Existing booking updated to cancelled → send cancellation notification
    """

    # Case 1 — New booking created
    if created:
        Notification.objects.create(
            user=instance.user,
            title="Booking Confirmed ✅",
            message=f"Your booking #{instance.id} has been confirmed. "
            f"Total amount: ₹{instance.total_amount}.",
        )

    # Case 2 — Existing booking was cancelled
    elif instance.booking_status == "cancelled":
        Notification.objects.create(
            user=instance.user,
            title="Booking Cancelled ❌",
            message=f"Your booking #{instance.id} has been cancelled. "
            f"We hope to see you again soon!",
        )

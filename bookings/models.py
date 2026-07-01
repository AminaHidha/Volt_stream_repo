from django.db import models

from slots.models import Slot
from users.models import User


class BookingManager(models.Manager):
    """
    Custom Model Manager for Booking.

    Instead of writing Booking.objects.filter(booking_status='confirmed')
    everywhere in your code, you can now write Booking.objects.confirmed()

    This is cleaner, reusable, and easier to maintain.
    If you ever change the status name, you only change it here — not everywhere.
    """

    def confirmed(self):
        """Returns all confirmed bookings."""
        return self.filter(booking_status="confirmed")

    def cancelled(self):
        """Returns all cancelled bookings."""
        return self.filter(booking_status="cancelled")

    def pending(self):
        """Returns all pending bookings."""
        return self.filter(booking_status="pending")

    def completed(self):
        """Returns all completed bookings."""
        return self.filter(booking_status="completed")

    def for_user(self, user):
        """Returns all bookings for a specific user."""
        return self.filter(user=user)

    def active(self):
        """
        Returns bookings that are either confirmed or pending.
        These are bookings that are still ongoing.
        """
        return self.filter(booking_status__in=["confirmed", "pending"])


class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")

    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name="bookings")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    booking_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="confirmed",
        db_index=True,  # ✅ frequently filtered (confirmed/cancelled/pending)
    )

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True  # ✅ used for ordering bookings by recency
    )

    objects = BookingManager()

    class Meta:
        indexes = [
            models.Index(
                fields=["user", "booking_status"]
            ),  # ✅ for_user() + status filtering together
        ]

    def __str__(self):
        return f"{self.user.email} - {self.slot.id}"

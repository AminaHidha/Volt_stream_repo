from django.db import models
from users.models import User


class OwnerProfile(models.Model):

    APPROVAL_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="owner_profile"
    )

    business_name = models.CharField(max_length=200)
    station_name = models.CharField(max_length=200)
    station_address = models.TextField()
    license_number = models.CharField(max_length=100)

    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_CHOICES, default="pending"
    )

    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # MFA Fields
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True, default="")

    def __str__(self):
        return self.station_name
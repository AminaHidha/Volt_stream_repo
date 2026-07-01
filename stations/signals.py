from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from stations.models import ChargingStation


@receiver(post_save, sender=ChargingStation)
def station_notification(sender, instance, created, **kwargs):
    """
    Fires automatically AFTER a station is saved to database.

    When owner creates a new station → notify them it's under review.
    """

    if created:
        Notification.objects.create(
            user=instance.owner,
            title="Station Created 🏗️",
            message=f"Your station '{instance.station_name}' has been created "
            f"successfully and is now active.",
        )

from rest_framework.response import Response
from rest_framework import status

from notifications.models import Notification


def create_notification_service(
    user,
    title,
    message
):

    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message
    )

    return notification
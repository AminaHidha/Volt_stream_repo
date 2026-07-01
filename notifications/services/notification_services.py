from notifications.models import Notification


def create_notification_service(user, title, message):

    notification = Notification.objects.create(user=user, title=title, message=message)

    return notification

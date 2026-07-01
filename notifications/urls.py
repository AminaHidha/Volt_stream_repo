from django.urls import path

from .views import (DeleteNotificationView, MarkNotificationReadView,
                    NotificationDetailView, NotificationListView)

urlpatterns = [
    path("", NotificationListView.as_view()),
    path("<int:notification_id>/", NotificationDetailView.as_view()),
    path("<int:notification_id>/read/", MarkNotificationReadView.as_view()),
    path("<int:notification_id>/delete/", DeleteNotificationView.as_view()),
]

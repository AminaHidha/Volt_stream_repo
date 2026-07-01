from django.urls import path

from .views import (ChargerCreateView, ChargerDeleteView, ChargerDetailView,
                    ChargerListView, ChargerStatusUpdateView,
                    ChargerUpdateView)

urlpatterns = [
    path("create/", ChargerCreateView.as_view()),
    path("station/<int:station_id>/", ChargerListView.as_view()),
    path("<int:charger_id>/", ChargerDetailView.as_view()),
    path("<int:charger_id>/update/", ChargerUpdateView.as_view()),
    path("<int:charger_id>/delete/", ChargerDeleteView.as_view()),
    path("<int:charger_id>/status/", ChargerStatusUpdateView.as_view()),
]

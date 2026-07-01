from django.urls import path

from .views import (ChargerSlotsView, SlotCreateView, SlotDeleteView,
                    SlotUpdateView)

urlpatterns = [
    path("create/", SlotCreateView.as_view()),
    path("charger/<int:charger_id>/", ChargerSlotsView.as_view()),
    path("<int:slot_id>/update/", SlotUpdateView.as_view()),
    path("<int:slot_id>/delete/", SlotDeleteView.as_view()),
]

from django.urls import path

from .views import (
    StationListCreateView,
    StationDetailView
)

urlpatterns = [

    path(
        "",
        StationListCreateView.as_view()
    ),

    path(
        "<int:pk>/",
        StationDetailView.as_view()
    ),
]
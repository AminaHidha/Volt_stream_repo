from django.urls import path

from .views import (PublicStationListNoAuthView, PublicStationListView,
                    StationDetailView, StationListCreateView)

urlpatterns = [
    path("", StationListCreateView.as_view()),
    path("<int:pk>/", StationDetailView.as_view()),
    path("public/", PublicStationListView.as_view()),
    path("list/", PublicStationListNoAuthView.as_view()),
]

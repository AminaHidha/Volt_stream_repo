from django.urls import path

from .views import (CreateReviewView, MyReviewsView, StationAverageRatingView,
                    StationReviewsView)

urlpatterns = [
    path("create/", CreateReviewView.as_view()),
    path("my/", MyReviewsView.as_view()),
    path("station/<int:station_id>/", StationReviewsView.as_view()),
    path("station/<int:station_id>/average/", StationAverageRatingView.as_view()),
]

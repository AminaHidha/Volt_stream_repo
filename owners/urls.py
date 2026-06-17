from django.urls import path
from .views import (
    OwnerSetupView,
    OwnerProfileView,
    OwnerProfileUpdateView,
    OwnerDashboardView,
    )

urlpatterns=[
    path("setup/",OwnerSetupView.as_view()),
    path("profile/",OwnerProfileView.as_view()),
    path("profile/update/",OwnerProfileUpdateView.as_view()),
    path("dashboard/",OwnerDashboardView.as_view()),
]
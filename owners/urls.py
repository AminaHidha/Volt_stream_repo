from django.urls import path
from .views import (
    OwnerDashboardView,
    OwnerProfileUpdateView,
    OwnerProfileView,
    OwnerSetupView,
    MFASetupView,
    MFAVerifyEnableView,
    MFADisableView,
    MFALoginVerifyView,
)

urlpatterns = [
    path("setup/", OwnerSetupView.as_view()),
    path("profile/", OwnerProfileView.as_view()),
    path("profile/update/", OwnerProfileUpdateView.as_view()),
    path("dashboard/", OwnerDashboardView.as_view()),

    # MFA endpoints
    path("mfa/setup/", MFASetupView.as_view()),
    path("mfa/enable/", MFAVerifyEnableView.as_view()),
    path("mfa/disable/", MFADisableView.as_view()),
    path("mfa/verify/", MFALoginVerifyView.as_view()),
]
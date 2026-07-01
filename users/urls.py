from django.urls import path

from .views import (GoogleLoginView, LoginUserView, LogoutView, ProfileView,
                    RegisterUserView, ResendOTPView, SaveFCMTokenView,
                    VerifyGoogleOTPView, VerifyOTPView)

urlpatterns = [
    # Auth
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("verify-google-otp/", VerifyGoogleOTPView.as_view(), name="verify-google-otp"),
    # OTP
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    # Auth
    path("logout/", LogoutView.as_view(), name="logout"),
    # FCM Token
    path("save-fcm-token/", SaveFCMTokenView.as_view(), name="save-fcm-token"),
    path("profile/", ProfileView.as_view(), name="profile"),
]

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.services.recaptcha_service import verify_recaptcha

from .serializers import (LoginSerializer, LogoutSerializer,
                          RegisterSerializer, ResendOTPSerializer,
                          VerifyOTPSerializer)
from .services.auth_services import (google_login_service, login_user_service,
                                     logout_user_service,
                                     register_user_service, resend_otp_service,
                                     verify_google_otp_service,
                                     verify_login_otp_service,
                                     verify_register_otp_service)


class RegisterUserView(APIView):

    @extend_schema(request=RegisterSerializer)
    def post(self, request):

        if getattr(request, "limited", False):
            return Response(
                {"error": "Too many registration attempts."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        recaptcha_token = request.data.get("recaptcha_token")
        if not verify_recaptcha(recaptcha_token):
            return Response(
                {"error": "reCAPTCHA verification failed. Are you a bot?"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data.pop("recaptcha_token", None)

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            return register_user_service(serializer.validated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):

    @extend_schema(request=LoginSerializer)
    def post(self, request):

        if getattr(request, "limited", False):
            return Response(
                {"error": "Too many login attempts. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        recaptcha_token = request.data.get("recaptcha_token")
        if not verify_recaptcha(recaptcha_token):
            return Response(
                {"error": "reCAPTCHA verification failed. Are you a bot?"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data.pop("recaptcha_token", None)

        serializer = LoginSerializer(data=data)

        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            return login_user_service(phone)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """Verify OTP for both register and login."""

    @extend_schema(request=VerifyOTPSerializer)
    def post(self, request):

        serializer = VerifyOTPSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            otp_code = serializer.validated_data["otp_code"]
            purpose = request.data.get("purpose", "register")

            if purpose == "login":
                return verify_login_otp_service(phone, otp_code)
            else:
                return verify_register_otp_service(phone, otp_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):

    @extend_schema(request=ResendOTPSerializer)
    def post(self, request):

        serializer = ResendOTPSerializer(data=request.data)

        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            purpose = serializer.validated_data["purpose"]
            return resend_otp_service(phone, purpose)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(APIView):

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"token": {"type": "string"}},
            }
        }
    )
    def post(self, request):
        token = request.data.get("token")
        return google_login_service(token)


class LogoutView(APIView):

    @extend_schema(request=LogoutSerializer)
    def post(self, request):

        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():
            refresh = serializer.validated_data["refresh"]
            return logout_user_service(refresh)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyGoogleOTPView(APIView):

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "otp_code": {"type": "string"},
                },
            }
        }
    )
    def post(self, request):
        email = request.data.get("email")
        otp_code = request.data.get("otp_code")
        return verify_google_otp_service(email, otp_code)


# ========================
# SAVE FCM TOKEN
# ========================


class SaveFCMTokenView(APIView):
    """
    Save Firebase FCM token for the logged in user.
    Frontend calls this after getting the token from Firebase.
    POST /api/save-fcm-token/
    Body: { "fcm_token": "..." }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        fcm_token = request.data.get("fcm_token")

        if not fcm_token:
            return Response(
                {"error": "fcm_token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        request.user.fcm_token = fcm_token
        request.user.save(update_fields=["fcm_token"])

        return Response(
            {"message": "FCM token saved successfully"}, status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": str(user.id),
                "username": user.username,
                "phone": user.phone,
                "role": user.role,
                "is_verified": user.is_verified,
                "owner_verification_status": user.owner_verification_status,
            }
        )

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import OwnerProfile
from .serializers import OwnerProfileSerializer
from .services.owner_services import create_owner_profile_service
from .services.mfa_services import generate_mfa_secret, generate_qr_code, verify_totp


class OwnerSetupView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OwnerProfileSerializer)
    def post(self, request):
        serializer = OwnerProfileSerializer(data=request.data)
        if serializer.is_valid():
            return create_owner_profile_service(request.user, serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OwnerProfileSerializer(profile)
        return Response(serializer.data)


class OwnerProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OwnerProfileSerializer)
    def put(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OwnerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({
            "business_name": profile.business_name,
            "station_name": profile.station_name,
            "approval_status": profile.approval_status,
            "submitted_at": profile.submitted_at,
            "mfa_enabled": profile.mfa_enabled,
        })


# ========================
# MFA VIEWS
# ========================

class MFASetupView(APIView):
    """
    Step 1 of MFA setup.
    Owner calls this to get a QR code to scan with
    Google Authenticator app.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        secret = generate_mfa_secret()
        profile.mfa_secret = secret
        profile.save()

        qr_code = generate_qr_code(secret, request.user.phone)

        return Response({
            "message": "Scan this QR code with Google Authenticator",
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code}",
        })


class MFAVerifyEnableView(APIView):
    """
    Step 2 of MFA setup.
    Owner scans QR code then enters the 6-digit code here.
    If correct, MFA is enabled on their account.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string', 'example': '123456'}
                },
                'required': ['code']
            }
        }
    )
    def post(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        code = request.data.get("code")

        if not code:
            return Response(
                {"error": "Please provide the 6-digit code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not profile.mfa_secret:
            return Response(
                {"error": "Please generate QR code first via GET /api/owners/mfa/setup/"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if verify_totp(profile.mfa_secret, code):
            profile.mfa_enabled = True
            profile.save()
            return Response({
                "message": "MFA enabled successfully! Your account is now protected."
            })

        return Response(
            {"error": "Invalid code. Please try again."},
            status=status.HTTP_400_BAD_REQUEST
        )


class MFADisableView(APIView):
    """
    Disable MFA for the owner.
    Owner must provide a valid TOTP code to confirm.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string', 'example': '123456'}
                },
                'required': ['code']
            }
        }
    )
    def post(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        code = request.data.get("code")

        if not code:
            return Response(
                {"error": "Please provide the 6-digit code to disable MFA"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not profile.mfa_enabled:
            return Response(
                {"error": "MFA is not enabled on your account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if verify_totp(profile.mfa_secret, code):
            profile.mfa_enabled = False
            profile.mfa_secret = ""
            profile.save()
            return Response({"message": "MFA disabled successfully."})

        return Response(
            {"error": "Invalid code. MFA not disabled."},
            status=status.HTTP_400_BAD_REQUEST
        )


class MFALoginVerifyView(APIView):
    """
    Called during owner login when MFA is enabled.
    After phone OTP is verified, owner must also enter
    the 6-digit Google Authenticator code here.
    """

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'phone': {'type': 'string', 'example': '9876543210'},
                    'code': {'type': 'string', 'example': '123456'}
                },
                'required': ['phone', 'code']
            }
        }
    )
    def post(self, request):
        phone = request.data.get("phone")
        code = request.data.get("code")

        if not phone or not code:
            return Response(
                {"error": "Phone and code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from users.models import User
            user = User.objects.get(phone=phone)
            profile = user.owner_profile
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not profile.mfa_enabled:
            return Response(
                {"error": "MFA is not enabled for this account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if verify_totp(profile.mfa_secret, code):
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "MFA verified. Login successful!",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "phone": user.phone,
                    "role": user.role,
                    "is_verified": user.is_verified,
                }
            })

        return Response(
            {"error": "Invalid MFA code. Please try again."},
            status=status.HTTP_400_BAD_REQUEST
        )
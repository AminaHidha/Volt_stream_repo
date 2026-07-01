import random

from django.conf import settings
from django.core.mail import send_mail
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import OTP, User
from users.services.otp_services import create_otp


def register_user_service(validated_data):
    """
    Register user with username and phone only.
    No password needed.
    Sends OTP to phone for verification.
    """
    phone = validated_data.get("phone")
    username = validated_data.get("username")
    role = validated_data.get("role", "driver")

    user = User(
        phone=phone,
        username=username,
        role=role,
        is_verified=False,
    )

    # No password — set unusable password
    user.set_unusable_password()

    if role == "owner":
        user.owner_verification_status = "pending"
    else:
        user.owner_verification_status = "approved"

    user.save()

    # Send OTP to phone
    create_otp(user, "register")

    return Response(
        {
            "message": "Registration successful. OTP sent to your phone.",
            "phone": user.phone,
            "role": user.role,
        },
        status=status.HTTP_201_CREATED,
    )


def login_user_service(phone):
    """
    Flipkart style login.
    User enters phone → OTP sent → user verifies OTP → logged in.
    No password needed.
    """
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response(
            {"error": "No account found with this phone number"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Owner check
    if user.role == "owner":
        if user.owner_verification_status == "pending":
            return Response(
                {"error": "Waiting for admin approval", "status": "pending"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.owner_verification_status == "rejected":
            return Response(
                {"error": "Owner account rejected", "status": "rejected"},
                status=status.HTTP_403_FORBIDDEN,
            )

    # Send OTP to phone
    create_otp(user, "login")

    return Response(
        {
            "message": "OTP sent to your phone",
            "phone": phone,
        },
        status=status.HTTP_200_OK,
    )


def verify_register_otp_service(phone, otp_code):
    """
    Verify OTP sent during registration.
    After verification, user is marked as verified and logged in.
    """
    from users.services.otp_services import verify_otp_by_phone

    success, result = verify_otp_by_phone(phone, otp_code, "register")

    if not success:
        return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)

    user = result
    user.is_verified = True
    user.save()

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "message": "OTP verified successfully",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "username": user.username,
                "phone": user.phone,
                "role": user.role,
                "is_verified": user.is_verified,
            },
        },
        status=status.HTTP_200_OK,
    )


def verify_login_otp_service(phone, otp_code):
    """
    Verify OTP sent during login.
    After verification, user gets JWT tokens.
    """
    from users.services.otp_services import verify_otp_by_phone

    success, result = verify_otp_by_phone(phone, otp_code, "login")

    if not success:
        return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)

    user = result

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "message": "Login successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "username": user.username,
                "phone": user.phone,
                "role": user.role,
                "is_verified": user.is_verified,
                "owner_verification_status": user.owner_verification_status,
            },
        },
        status=status.HTTP_200_OK,
    )


def resend_otp_service(phone, purpose):
    from users.services.otp_services import resend_otp_by_phone

    success, message = resend_otp_by_phone(phone, purpose)

    if not success:
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": message}, status=status.HTTP_200_OK)


def logout_user_service(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT
        )
    except TokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


def google_login_service(token):
    try:
        google_request = google_requests.Request()
        info = id_token.verify_oauth2_token(
            token, google_request, settings.GOOGLE_CLIENT_ID, clock_skew_in_seconds=10
        )

        email = info.get("email")
        full_name = info.get("name", "")

        if not email:
            return Response(
                {"error": "Email not found in token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = email.lower()
        user = User.objects.filter(email=email).first()

        if user:
            if user.role == "admin":
                return Response(
                    {"error": "Google login not allowed for admin"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if user.role == "owner":
                return Response(
                    {"error": "Google login not allowed for owner"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not user.is_verified:
                user.is_verified = True
                user.save()
        else:
            user = User.objects.create(
                email=email,
                username=full_name,
                full_name=full_name,
                role="driver",
                phone="",
                is_verified=True,
                owner_verification_status="approved",
            )
            user.set_unusable_password()
            user.save()

        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, purpose="google_login", otp_code=otp_code)

        send_mail(
            "Google Login OTP",
            f"Your OTP is {otp_code}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "OTP sent successfully", "email": user.email},
            status=status.HTTP_200_OK,
        )

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": f"Google auth failed: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


def verify_google_otp_service(email, otp_code):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    otp = OTP.objects.filter(
        user=user, purpose="google_login", otp_code=otp_code, is_used=False
    ).first()

    if not otp:
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

    if otp.is_expired():
        return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

    otp.is_used = True
    otp.save()

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "message": "Google MFA Login Successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
        },
        status=status.HTTP_200_OK,
    )

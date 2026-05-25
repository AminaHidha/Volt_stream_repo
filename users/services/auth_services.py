from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from users.models import User
from users.services.otp_services import create_otp
from rest_framework_simplejwt.exceptions import TokenError


def login_user_service(email, password):

    user = authenticate(
        email=email,
        password=password
    )

    if user is None:
        return Response({
            "error": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # EMAIL NOT VERIFIED
    if not user.is_verified:

        create_otp(user, "register")

        return Response({
            "error": "Email not verified",
            "email": user.email,
            "redirect": "verify-otp"
        }, status=status.HTTP_403_FORBIDDEN)

    # OWNER CHECK
    if user.role == "owner":

        if user.owner_verification_status == "pending":

            return Response({
                "error": "Waiting for admin approval",
                "status": "pending"
            }, status=status.HTTP_403_FORBIDDEN)

        if user.owner_verification_status == "rejected":

            return Response({
                "error": "Owner account rejected",
                "status": "rejected"
            }, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)

    return Response({

        "message": "Login successful",

        "refresh": str(refresh),

        "access": str(refresh.access_token),

        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_verified": user.is_verified,
            "owner_verification_status":
                user.owner_verification_status,
        }

    }, status=status.HTTP_200_OK)


def register_user_service(validated_data):

    password = validated_data.pop("password")

    user = User(**validated_data)

    user.set_password(password)

    user.is_verified = False

    # OWNER
    if user.role == "owner":
        user.owner_verification_status = "pending"

    # DRIVER
    else:
        user.owner_verification_status = "approved"

    user.save()

    create_otp(user, "register")

    return Response({
        "message":
            "Registration successful. OTP sent.",
        "email": user.email,
        "role": user.role,
    }, status=status.HTTP_201_CREATED)


def verify_register_otp_service(email, otp_code):

    from users.services.otp_services import verify_otp

    success, result = verify_otp(
        email,
        otp_code,
        "register"
    )

    if not success:

        return Response({
            "error": result
        }, status=status.HTTP_400_BAD_REQUEST)

    user = result

    user.is_verified = True

    user.save()

    refresh = RefreshToken.for_user(user)

    return Response({

        "message": "OTP verified successfully",

        "refresh": str(refresh),

        "access": str(refresh.access_token),

        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_verified": user.is_verified,
            "owner_verification_status":
                user.owner_verification_status,
        }

    }, status=status.HTTP_200_OK)


def forgot_password_service(email):

    try:
        user = User.objects.get(email=email)

    except User.DoesNotExist:

        return Response({
            "message":
                "If email exists, OTP sent."
        }, status=status.HTTP_200_OK)

    create_otp(user, "forgot_password")

    return Response({
        "message": "OTP sent",
        "email": email,
    }, status=status.HTTP_200_OK)


def reset_password_service(
    email,
    otp_code,
    new_password
):

    from users.services.otp_services import verify_otp

    success, result = verify_otp(
        email,
        otp_code,
        "forgot_password"
    )

    if not success:

        return Response({
            "error": result
        }, status=status.HTTP_400_BAD_REQUEST)

    user = result

    user.set_password(new_password)

    user.save()

    return Response({
        "message": "Password reset successful"
    }, status=status.HTTP_200_OK)


def resend_otp_service(email, purpose):

    from users.services.otp_services import resend_otp

    success, message = resend_otp(
        email,
        purpose
    )

    if not success:

        return Response({
            "error": message
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": message
    }, status=status.HTTP_200_OK)


def google_login_service(token):

    try:

        google_request = google_requests.Request()

        info = id_token.verify_oauth2_token(
            token,
            google_request,
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )

        email = info.get("email")

        full_name = info.get("name", "")

        if not email:

            return Response({
                "error":
                    "Email not found in token"
            }, status=status.HTTP_400_BAD_REQUEST)

        email = email.lower()

        user = User.objects.filter(
            email=email
        ).first()

        if user:

            if user.role == "admin":

                return Response({
                    "error":
                        "Google login not allowed for admin"
                }, status=status.HTTP_403_FORBIDDEN)

            if user.role == "owner":

                return Response({
                    "error":
                        "Google login not allowed for owner"
                }, status=status.HTTP_403_FORBIDDEN)

            if not user.is_verified:

                user.is_verified = True
                user.save()

        else:

            user = User.objects.create(
                email=email,
                full_name=full_name,
                role="driver",
                phone="",
                is_verified=True,
                owner_verification_status="approved"
            )

        refresh = RefreshToken.for_user(user)

        return Response({

            "message": "Google login successful",

            "access":
                str(refresh.access_token),

            "refresh":
                str(refresh),

            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
                "is_verified":
                    user.is_verified,
                "owner_verification_status":
                    user.owner_verification_status,
            }

        }, status=status.HTTP_200_OK)

    except ValueError as e:

        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:

        return Response({
            "error":
                f"Google auth failed: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)


def logout_user_service(refresh_token):

    try:

        token = RefreshToken(refresh_token)

        token.blacklist()

        return Response({
            "message": "Logout successful"
        }, status=status.HTTP_205_RESET_CONTENT)

    except TokenError:

        return Response({
            "error": "Invalid token"
        }, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration only needs username and phone.
    No password, no email.
    """

    class Meta:
        model = User
        fields = [
            "username",
            "phone",
            "role",
        ]

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if len(value) < 10:
            raise serializers.ValidationError("Phone number is too short")
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value


class LoginSerializer(serializers.Serializer):
    """
    Login only needs phone number.
    OTP will be sent to that phone.
    """

    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6, min_length=6)


class ResendOTPSerializer(serializers.Serializer):

    PURPOSE_CHOICES = (
        ("register", "Register"),
        ("login", "Login"),
        ("forgot_password", "Forgot Password"),
    )

    phone = serializers.CharField(max_length=15)
    purpose = serializers.ChoiceField(choices=PURPOSE_CHOICES)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User

        fields = [
            'full_name',
            'email',
            'password',
            'phone',
            'role'
        ]

    # =========================
    # EMAIL VALIDATION
    # =========================
    def validate_email(self, value):

        value = value.lower()

        if User.objects.filter(email=value).exists():

            raise serializers.ValidationError(
                'Email already exists'
            )

        return value

    # =========================
    # PHONE VALIDATION
    # =========================
    def validate_phone(self, value):

        if not value.isdigit():

            raise serializers.ValidationError(
                'Phone number must contain only digits'
            )

        if len(value) < 10:

            raise serializers.ValidationError(
                'Phone number is too short'
            )

        return value

    # =========================
    # PASSWORD VALIDATION
    # =========================
    def validate_password(self, value):

        validate_password(value)

        return value

    # =========================
    # CREATE USER
    # =========================
    def create(self, validated_data):

        password = validated_data.pop('password')

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        return user
        

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, min_length=6)


class ResendOTPSerializer(serializers.Serializer):

    PURPOSE_CHOICES = (
        ('register', 'Register'),
        ('forgot_password', 'Forgot Password'),
    )

    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=PURPOSE_CHOICES)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()
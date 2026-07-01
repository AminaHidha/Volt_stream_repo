from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):

        if not phone:
            raise ValueError("Phone number is required")

        user = self.model(phone=phone, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("owner_verification_status", "approved")

        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):

    ROLE_CHOICES = (
        ("driver", "Driver"),
        ("owner", "Owner"),
        ("admin", "Admin"),
    )

    # Remove default username field
    username = models.CharField(max_length=150, blank=True, null=True, default=None)

    full_name = models.CharField(max_length=150, blank=True, default="")

    # Email is now optional — only needed for Google login
    email = models.EmailField(blank=True, default="", unique=False)

    # Phone is now the unique identifier
    phone = models.CharField(max_length=15, unique=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="driver")

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    owner_verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    # ========================
    # FCM TOKEN — Firebase
    # Push Notification token
    # saved from browser
    # ========================
    fcm_token = models.CharField(max_length=500, blank=True, null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)

    # Phone is now the login field
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone


class OTP(models.Model):

    PURPOSE_CHOICES = (
        ("register", "Register"),
        ("login", "Login"),
        ("forgot_password", "Forgot Password"),
        ("google_login", "Google Login"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")

    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)

    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    resend_count = models.IntegerField(default=0)

    last_resend_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > (self.created_at + timedelta(minutes=10))

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    def __str__(self):
        return f"{self.user.phone} - {self.purpose}"

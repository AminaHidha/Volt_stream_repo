from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


class UserRegistrationTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/register/"
        self.client.defaults["SERVER_NAME"] = "localhost"

    @patch("users.views.verify_recaptcha", return_value=True)
    @patch("users.services.auth_services.create_otp")
    def test_register_success(self, mock_otp, mock_recaptcha):
        """
        Test that a new user can register successfully.
        Expected: 201 Created
        """
        data = {
            "username": "testuser",
            "phone": "9876543210",
            "role": "driver",
            "recaptcha_token": "fake-token",
        }
        response = self.client.post(
            self.register_url, data, format="json", SERVER_NAME="localhost"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("users.views.verify_recaptcha", return_value=True)
    @patch("users.services.auth_services.create_otp")
    def test_register_duplicate_phone(self, mock_otp, mock_recaptcha):
        """
        Test that registering with existing phone fails.
        Expected: 400 Bad Request
        """
        User.objects.create_user(
            phone="9876543210",
            username="existinguser",
            role="driver",
        )
        data = {
            "username": "anotheruser",
            "phone": "9876543210",
            "role": "driver",
            "recaptcha_token": "fake-token",
        }
        response = self.client.post(
            self.register_url, data, format="json", SERVER_NAME="localhost"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("users.views.verify_recaptcha", return_value=False)
    def test_register_fails_without_recaptcha(self, mock_recaptcha):
        """
        Test that registration fails when reCAPTCHA is invalid.
        Expected: 400 Bad Request
        """
        data = {
            "username": "botuser",
            "phone": "9876543299",
            "role": "driver",
            "recaptcha_token": "invalid-token",
        }
        response = self.client.post(
            self.register_url, data, format="json", SERVER_NAME="localhost"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class UserLoginTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.login_url = "/api/login/"
        self.client.defaults["SERVER_NAME"] = "localhost"

        self.user = User.objects.create_user(
            phone="9876543210",
            username="logintestuser",
            role="driver",
        )
        self.user.is_verified = True
        self.user.owner_verification_status = "approved"
        self.user.save()

    @patch("users.services.auth_services.create_otp")
    @patch("users.views.verify_recaptcha", return_value=True)
    def test_login_success(self, mock_recaptcha, mock_otp):
        """
        Test that a registered user can request login OTP successfully.
        Expected: 200 OK
        """
        data = {
            "phone": "9876543210",
            "recaptcha_token": "fake-token",
        }
        response = self.client.post(
            self.login_url, data, format="json", SERVER_NAME="localhost"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("users.views.verify_recaptcha", return_value=True)
    def test_login_wrong_phone(self, mock_recaptcha):
        """
        Test that login fails with non-existent phone.
        Expected: 400 or 401 or 404
        """
        data = {
            "phone": "9999999999",
            "recaptcha_token": "fake-token",
        }
        response = self.client.post(
            self.login_url, data, format="json", SERVER_NAME="localhost"
        )
        self.assertIn(
            response.status_code,
            [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_404_NOT_FOUND,
            ],
        )

    @patch("users.views.verify_recaptcha", return_value=False)
    def test_login_fails_without_recaptcha(self, mock_recaptcha):
        """
        Test that login fails when reCAPTCHA is invalid.
        Expected: 400 Bad Request
        """
        data = {
            "phone": "9876543210",
            "recaptcha_token": "invalid-token",
        }
        response = self.client.post(
            self.login_url, data, format="json", SERVER_NAME="localhost"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RecaptchaServiceTest(TestCase):

    @patch("users.services.recaptcha_service.requests.post")
    def test_recaptcha_returns_true_for_valid_token(self, mock_post):
        mock_post.return_value.json.return_value = {"success": True}
        from users.services.recaptcha_service import verify_recaptcha

        result = verify_recaptcha("valid-token")
        self.assertTrue(result)

    @patch("users.services.recaptcha_service.requests.post")
    def test_recaptcha_returns_false_for_invalid_token(self, mock_post):
        mock_post.return_value.json.return_value = {"success": False}
        from users.services.recaptcha_service import verify_recaptcha

        result = verify_recaptcha("invalid-token")
        self.assertFalse(result)

    def test_recaptcha_returns_false_for_empty_token(self):
        from users.services.recaptcha_service import verify_recaptcha

        result = verify_recaptcha("")
        self.assertFalse(result)
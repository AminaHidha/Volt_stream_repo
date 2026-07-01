from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from bookings.models import Booking
from chargers.models import Charger
from slots.models import Slot
from stations.models import ChargingStation
from users.models import User
from unittest.mock import patch


class BookingManagerTest(TestCase):
    """
    Tests for our Custom Model Manager methods.
    """

    def setUp(self):
        """Create test data for all booking manager tests."""

        self.user = User.objects.create_user(
            email="manager@gmail.com",
            password="Test1234@",
            full_name="Manager Test",
            phone="9876543210",
            role="driver",
        )

        self.station = ChargingStation.objects.create(
            owner=self.user,
            station_name="Test Station",
            address="Test Address",
            city="Test City",
            latitude=10.000000,
            longitude=76.000000,
            opening_time="08:00:00",
            closing_time="20:00:00",
        )

        self.charger = Charger.objects.create(
            station=self.station,
            charger_name="Test Charger",
            charger_type="AC",
            power_output=7,
            price_per_kwh=10,
            status="available",
        )

        self.slot = Slot.objects.create(
            charger=self.charger,
            start_time="2026-06-25T10:00:00Z",
            end_time="2026-06-25T11:00:00Z",
            is_booked=False,
        )

        # Create bookings with different statuses
        self.confirmed_booking = Booking.objects.create(
            user=self.user, slot=self.slot, total_amount=100, booking_status="confirmed"
        )

        self.slot2 = Slot.objects.create(
            charger=self.charger,
            start_time="2026-06-25T11:00:00Z",
            end_time="2026-06-25T12:00:00Z",
            is_booked=False,
        )

        self.cancelled_booking = Booking.objects.create(
            user=self.user,
            slot=self.slot2,
            total_amount=100,
            booking_status="cancelled",
        )

    def test_confirmed_manager(self):
        """Test Booking.objects.confirmed() returns only confirmed bookings."""
        confirmed = Booking.objects.confirmed()
        self.assertEqual(confirmed.count(), 1)
        self.assertEqual(confirmed.first().booking_status, "confirmed")

    def test_cancelled_manager(self):
        """Test Booking.objects.cancelled() returns only cancelled bookings."""
        cancelled = Booking.objects.cancelled()
        self.assertEqual(cancelled.count(), 1)
        self.assertEqual(cancelled.first().booking_status, "cancelled")

    def test_active_manager(self):
        """Test Booking.objects.active() returns confirmed + pending bookings."""
        active = Booking.objects.active()
        self.assertEqual(active.count(), 1)

    def test_for_user_manager(self):
        """Test Booking.objects.for_user() returns bookings for specific user."""
        bookings = Booking.objects.for_user(self.user)
        self.assertEqual(bookings.count(), 2)


class BookingAPITest(TestCase):
    """
    Tests for booking API endpoints.
    """

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="bookingapi@gmail.com",
            password="Test1234@",
            full_name="Booking API Test",
            phone="9876543210",
            role="driver",
        )
        self.user.is_verified = True
        self.user.save()

        # Authenticate the client
        self.client.force_authenticate(user=self.user)

        self.station = ChargingStation.objects.create(
            owner=self.user,
            station_name="API Test Station",
            address="Test Address",
            city="Test City",
            latitude=10.000000,
            longitude=76.000000,
            opening_time="08:00:00",
            closing_time="20:00:00",
        )

        self.charger = Charger.objects.create(
            station=self.station,
            charger_name="API Test Charger",
            charger_type="AC",
            power_output=7,
            price_per_kwh=10,
            status="available",
        )

        self.slot = Slot.objects.create(
            charger=self.charger,
            start_time="2026-06-25T10:00:00Z",
            end_time="2026-06-25T11:00:00Z",
            is_booked=False,
        )

        @patch("bookings.services.booking_services.send_booking_confirmation_sms.delay")
        def test_create_booking_success(self, mock_sms):
            """
            Test that authenticated user can create a booking.
            Expected: 201 Created
            """
            data = {"slot": self.slot.id, "total_amount": 100}
            response = self.client.post("/api/bookings/create/", data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn("booking_id", response.data)

    def test_create_booking_already_booked_slot(self):
        """
        Test that booking an already booked slot fails.
        Expected: 400 Bad Request
        """
        self.slot.is_booked = True
        self.slot.save()

        data = {"slot": self.slot.id, "total_amount": 100}
        response = self.client.post("/api/bookings/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_booking_unauthenticated(self):
        """
        Test that unauthenticated user cannot create a booking.
        Expected: 401 Unauthorized
        """
        # Remove authentication
        self.client.force_authenticate(user=None)

        data = {"slot": self.slot.id, "total_amount": 100}
        response = self.client.post("/api/bookings/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_my_bookings(self):
        """
        Test that user can get their own bookings.
        Expected: 200 OK
        """
        # Create a booking first
        Booking.objects.create(
            user=self.user, slot=self.slot, total_amount=100, booking_status="confirmed"
        )

        response = self.client.get("/api/bookings/my/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

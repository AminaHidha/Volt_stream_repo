from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Import Celery task
from bookings.tasks import send_cancellation_sms
from realtime.broadcast import broadcast_slot_update

from .models import Booking
from .serializers import BookingSerializer
from .services.booking_services import create_booking_service


class BookingCreateView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(request=BookingSerializer)
    def post(self, request):

        serializer = BookingSerializer(data=request.data)

        if serializer.is_valid():

            return create_booking_service(request.user, serializer.validated_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyBookingsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Using custom manager instead of filter()
        bookings = Booking.objects.for_user(request.user)

        serializer = BookingSerializer(bookings, many=True)

        return Response(serializer.data)


class BookingDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):

        try:
            # Using custom manager
            booking = Booking.objects.confirmed().get(id=booking_id, user=request.user)

        except Booking.DoesNotExist:

            return Response(
                {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookingSerializer(booking)

        return Response(serializer.data)


class CancelBookingView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, booking_id):

        try:
            # Using custom manager — only active bookings can be cancelled
            booking = Booking.objects.active().get(id=booking_id, user=request.user)

        except Booking.DoesNotExist:

            return Response(
                {"error": "Booking not found or already cancelled"},
                status=status.HTTP_404_NOT_FOUND,
            )

        booking.booking_status = "cancelled"
        booking.save()

        booking.slot.is_booked = False
        booking.slot.save()

        broadcast_slot_update(
            charger_id=booking.slot.charger_id, slot_id=booking.slot.id, is_booked=False
        )

        if request.user.phone:
            send_cancellation_sms.delay(phone=request.user.phone, booking_id=booking.id)

        return Response({"message": "Booking cancelled"})


class OwnerBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all bookings for slots belonging to this owner's chargers/stations
        bookings = (
            Booking.objects.filter(slot__charger__station__owner=request.user)
            .select_related("user", "slot", "slot__charger", "slot__charger__station")
            .order_by("-created_at")
        )

        data = []
        for booking in bookings:
            data.append(
                {
                    "id": booking.id,
                    "booking_status": booking.booking_status,
                    "total_amount": str(booking.total_amount),
                    "created_at": str(booking.created_at),
                    "user_phone": booking.user.phone,
                    "slot_id": booking.slot.id,
                    "start_time": str(booking.slot.start_time),
                    "end_time": str(booking.slot.end_time),
                    "charger_name": booking.slot.charger.charger_name,
                    "station_name": booking.slot.charger.station.station_name,
                }
            )

        return Response(data)

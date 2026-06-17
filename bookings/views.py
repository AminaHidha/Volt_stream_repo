from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from realtime.broadcast import broadcast_slot_update

from .models import Booking
from .serializers import BookingSerializer

from .services.booking_services import (
    create_booking_service
)

class BookingCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = BookingSerializer(
            data=request.data
        )

        if serializer.is_valid():

            return create_booking_service(
                request.user,
                serializer.validated_data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class MyBookingsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        bookings = Booking.objects.filter(
            user=request.user
        )

        serializer = BookingSerializer(
            bookings,
            many=True
        )

        return Response(serializer.data)
    
class BookingDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):

        try:

            booking = Booking.objects.get(
                id=booking_id,
                user=request.user
            )

        except Booking.DoesNotExist:

            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookingSerializer(
            booking
        )

        return Response(serializer.data)
    
class CancelBookingView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, booking_id):

        try:

            booking = Booking.objects.get(
                id=booking_id,
                user=request.user
            )

        except Booking.DoesNotExist:

            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        booking.booking_status = "cancelled"
        booking.save()

        booking.slot.is_booked = False
        booking.slot.save()

        broadcast_slot_update(
            charger_id=booking.slot.charger_id,
            slot_id=booking.slot.id,
            is_booked=False
        )

        return Response({
            "message": "Booking cancelled"
        })
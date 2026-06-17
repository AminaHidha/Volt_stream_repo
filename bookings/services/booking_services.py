from rest_framework.response import Response
from rest_framework import status
from realtime.broadcast import broadcast_slot_update

from bookings.models import Booking
from slots.models import Slot
from notifications.services.notification_services import (
    create_notification_service
)


def create_booking_service(user, validated_data):

    slot = validated_data["slot"]

    if slot.is_booked:

        return Response(
            {"error": "Slot already booked"},
            status=status.HTTP_400_BAD_REQUEST
        )

    booking = Booking.objects.create(
        user=user,
        slot=slot,
        total_amount=validated_data["total_amount"]
    )
    
    create_notification_service(
        user,
        "Booking Confirmed",
        "Your charging slot has been booked successfully."
)

    slot.is_booked = True
    slot.save()

    broadcast_slot_update(
    charger_id=slot.charger_id,
    slot_id=slot.id,
    is_booked=True
)

    return Response(
        {
            "message": "Booking created successfully",
            "booking_id": booking.id
        },
        status=status.HTTP_201_CREATED
    )
from rest_framework import status
from rest_framework.response import Response

from slots.models import Slot


def create_slot_service(validated_data):

    slot = Slot.objects.create(**validated_data)

    return Response(
        {"message": "Slot created successfully", "slot_id": slot.id},
        status=status.HTTP_201_CREATED,
    )


def get_charger_slots_service(charger_id):

    slots = Slot.objects.filter(charger_id=charger_id)

    data = []

    for slot in slots:

        data.append(
            {
                "id": slot.id,
                "charger": slot.charger.id,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "is_booked": slot.is_booked,
            }
        )

    return Response(data)


def update_slot_service(slot, validated_data):

    for key, value in validated_data.items():

        setattr(slot, key, value)

    slot.save()

    return Response({"message": "Slot updated successfully"})


def delete_slot_service(slot):

    slot.delete()

    return Response({"message": "Slot deleted successfully"})

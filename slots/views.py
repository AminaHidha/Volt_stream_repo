from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Slot
from .serializers import SlotSerializer

from .services.slot_services import (
    create_slot_service,
    get_charger_slots_service,
    update_slot_service,
    delete_slot_service
)


class SlotCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = SlotSerializer(
            data=request.data
        )

        if serializer.is_valid():

            return create_slot_service(
                serializer.validated_data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ChargerSlotsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, charger_id):

        return get_charger_slots_service(
            charger_id
        )


class SlotUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, slot_id):

        try:

            slot = Slot.objects.get(
                id=slot_id
            )

        except Slot.DoesNotExist:

            return Response(
                {"error": "Slot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SlotSerializer(
            slot,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            return update_slot_service(
                slot,
                serializer.validated_data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class SlotDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, slot_id):

        try:

            slot = Slot.objects.get(
                id=slot_id
            )

        except Slot.DoesNotExist:

            return Response(
                {"error": "Slot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return delete_slot_service(slot)
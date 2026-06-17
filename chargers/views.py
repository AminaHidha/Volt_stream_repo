from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Charger

from .serializers import ChargerSerializer
from .services.charger_services import (
    create_charger_service
)


class ChargerCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChargerSerializer(
            data=request.data
        )

        if serializer.is_valid():

            return create_charger_service(
                serializer.validated_data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ChargerListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, station_id):

        chargers = Charger.objects.filter(
            station_id=station_id
        )

        serializer = ChargerSerializer(
            chargers,
            many=True
        )

        return Response(serializer.data)


class ChargerDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, charger_id):

        try:
            charger = Charger.objects.get(
                id=charger_id
            )

        except Charger.DoesNotExist:

            return Response(
                {"error": "Charger not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChargerSerializer(charger)

        return Response(serializer.data)


class ChargerUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, charger_id):

        try:
            charger = Charger.objects.get(
                id=charger_id
            )

        except Charger.DoesNotExist:

            return Response(
                {"error": "Charger not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChargerSerializer(
            charger,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                "message": "Charger updated",
                "data": serializer.data
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ChargerDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, charger_id):

        try:
            charger = Charger.objects.get(
                id=charger_id
            )

        except Charger.DoesNotExist:

            return Response(
                {"error": "Charger not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        charger.delete()

        return Response({
            "message": "Charger deleted"
        })


class ChargerStatusUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, charger_id):

        try:
            charger = Charger.objects.get(
                id=charger_id
            )

        except Charger.DoesNotExist:

            return Response(
                {"error": "Charger not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        status_value = request.data.get("status")

        if status_value not in [
            "available",
            "busy",
            "offline"
        ]:
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        charger.status = status_value

        charger.save()

        return Response({
            "message": "Status updated",
            "status": charger.status
        })
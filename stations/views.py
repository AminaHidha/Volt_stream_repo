from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import ChargingStationSerializer

from .services.station_services import (
    create_station_service,
    get_owner_stations_service,
    update_station_service,
    delete_station_service
)


class StationListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return get_owner_stations_service(
            request.user
        )

    def post(self, request):

        serializer = ChargingStationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            return create_station_service(
                request.user,
                serializer.validated_data
            )

        from rest_framework.response import Response
        from rest_framework import status

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class StationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        serializer = ChargingStationSerializer(
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            return update_station_service(
                request.user,
                pk,
                serializer.validated_data
            )

        from rest_framework.response import Response
        from rest_framework import status

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):

        return delete_station_service(
            request.user,
            pk
        )
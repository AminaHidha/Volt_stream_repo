from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChargingStation
from .serializers import ChargingStationSerializer
from .services.station_services import (create_station_service,
                                        delete_station_service,
                                        get_owner_stations_service,
                                        update_station_service)


class StationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class StationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return get_owner_stations_service(request.user)

    @extend_schema(request=ChargingStationSerializer)
    def post(self, request):
        serializer = ChargingStationSerializer(data=request.data)
        if serializer.is_valid():
            return create_station_service(request.user, serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ChargingStationSerializer)
    def put(self, request, pk):
        serializer = ChargingStationSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            return update_station_service(request.user, pk, serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        return delete_station_service(request.user, pk)


class PublicStationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stations = ChargingStation.objects.filter(status="active").prefetch_related(
            "amenities"
        )

        city = request.query_params.get("city")
        search = request.query_params.get("search")

        if city:
            stations = stations.filter(city__icontains=city)
        if search:
            stations = stations.filter(station_name__icontains=search)

        paginator = StationPagination()
        page = paginator.paginate_queryset(stations, request)
        serializer = ChargingStationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PublicStationListNoAuthView(APIView):
    permission_classes = []

    def get(self, request):
        stations = ChargingStation.objects.filter(status="active").prefetch_related(
            "amenities"
        )

        paginator = StationPagination()
        page = paginator.paginate_queryset(stations, request)
        serializer = ChargingStationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

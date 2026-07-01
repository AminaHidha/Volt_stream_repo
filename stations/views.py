from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache

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
        # Clear station cache when new station created
        cache.delete("stations_public")
        serializer = ChargingStationSerializer(data=request.data)
        if serializer.is_valid():
            return create_station_service(request.user, serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ChargingStationSerializer)
    def put(self, request, pk):
        # Clear cache when station updated
        cache.delete("stations_public")
        cache.delete(f"station_detail_{pk}")
        serializer = ChargingStationSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            return update_station_service(request.user, pk, serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Clear cache when station deleted
        cache.delete("stations_public")
        cache.delete(f"station_detail_{pk}")
        return delete_station_service(request.user, pk)


class PublicStationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        city = request.query_params.get("city", "")
        search = request.query_params.get("search", "")
        page = request.query_params.get("page", "1")

        # ========================
        # BUILD CACHE KEY
        # ========================
        cache_key = f"stations_public_{city}_{search}_{page}"

        # ========================
        # CHECK CACHE FIRST
        # ========================
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"⚡ Cache HIT: {cache_key}")
            return Response(cached_data)

        print(f"🔍 Cache MISS: {cache_key} — querying database")

        # ========================
        # QUERY DATABASE
        # ========================
        stations = ChargingStation.objects.filter(
            status="active"
        ).prefetch_related("amenities")

        if city:
            stations = stations.filter(city__icontains=city)
        if search:
            stations = stations.filter(station_name__icontains=search)

        paginator = StationPagination()
        page_data = paginator.paginate_queryset(stations, request)
        serializer = ChargingStationSerializer(page_data, many=True)
        response = paginator.get_paginated_response(serializer.data)

        # ========================
        # SAVE TO CACHE — 5 mins
        # ========================
        cache.set(cache_key, response.data, timeout=300)
        print(f"✅ Cache SET: {cache_key}")

        return response


class PublicStationListNoAuthView(APIView):
    permission_classes = []

    def get(self, request):

        page = request.query_params.get("page", "1")
        cache_key = f"stations_noauth_{page}"

        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"⚡ Cache HIT: {cache_key}")
            return Response(cached_data)

        stations = ChargingStation.objects.filter(
            status="active"
        ).prefetch_related("amenities")

        paginator = StationPagination()
        page_data = paginator.paginate_queryset(stations, request)
        serializer = ChargingStationSerializer(page_data, many=True)
        response = paginator.get_paginated_response(serializer.data)

        cache.set(cache_key, response.data, timeout=300)
        print(f"✅ Cache SET: {cache_key}")

        return response
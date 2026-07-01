from rest_framework import status
from rest_framework.response import Response

from stations.models import ChargingStation


def create_station_service(owner, validated_data):
    station = ChargingStation.objects.create(owner=owner, **validated_data)
    return Response(
        {"message": "Station created successfully"}, status=status.HTTP_201_CREATED
    )


def get_owner_stations_service(owner):
    stations = ChargingStation.objects.filter(owner=owner).prefetch_related("amenities")

    data = []
    for station in stations:
        data.append(
            {
                "id": station.id,
                "station_name": station.station_name,
                "address": station.address,
                "city": station.city,
                "latitude": str(station.latitude),
                "longitude": str(station.longitude),
                "opening_time": str(station.opening_time),
                "closing_time": str(station.closing_time),
                "status": station.status,
                "amenities": [
                    {"id": a.id, "name": a.name} for a in station.amenities.all()
                ],
            }
        )

    return Response(data)


def update_station_service(owner, station_id, validated_data):
    try:
        station = ChargingStation.objects.get(id=station_id, owner=owner)
    except ChargingStation.DoesNotExist:
        return Response(
            {"error": "Station not found"}, status=status.HTTP_404_NOT_FOUND
        )

    for key, value in validated_data.items():
        setattr(station, key, value)

    station.save()

    return Response({"message": "Station updated successfully"})


def delete_station_service(owner, station_id):
    try:
        station = ChargingStation.objects.get(id=station_id, owner=owner)
    except ChargingStation.DoesNotExist:
        return Response(
            {"error": "Station not found"}, status=status.HTTP_404_NOT_FOUND
        )

    station.delete()

    return Response({"message": "Station deleted successfully"})

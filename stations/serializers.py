from rest_framework import serializers

from .models import Amenity, ChargingStation


class AmenitySerializer(serializers.ModelSerializer):
    """
    Serializer for Amenity model.
    Used to show amenity details inside station response.
    """

    class Meta:
        model = Amenity
        fields = ["id", "name"]


class ChargingStationSerializer(serializers.ModelSerializer):

    # This shows full amenity details when reading (GET)
    amenities = AmenitySerializer(many=True, read_only=True)

    # This accepts a list of amenity IDs when writing (POST/PUT)
    amenity_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Amenity.objects.all(),
        write_only=True,
        required=False,
        source="amenities",
    )

    class Meta:
        model = ChargingStation
        fields = [
            "id",
            "owner",
            "station_name",
            "address",
            "city",
            "latitude",
            "longitude",
            "opening_time",
            "closing_time",
            "status",
            "amenities",
            "amenity_ids",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "created_at",
        ]

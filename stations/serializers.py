from rest_framework import serializers
from .models import ChargingStation


class ChargingStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChargingStation

        fields = "__all__"

        read_only_fields = [
            "id",
            "owner",
            "created_at",
        ]
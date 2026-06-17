# chargers/serializers.py

from rest_framework import serializers
from .models import Charger


class ChargerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Charger

        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at"
        ]
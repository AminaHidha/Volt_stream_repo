from rest_framework import serializers
from .models import OwnerProfile


class OwnerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = OwnerProfile

        fields = [
            "business_name",
            "station_name",
            "station_address",
            "license_number",
        ]
# chargers/services/charger_services.py

from rest_framework import status
from rest_framework.response import Response

from chargers.models import Charger


def create_charger_service(validated_data):

    charger = Charger.objects.create(**validated_data)

    return Response(
        {"message": "Charger created successfully", "charger_id": charger.id},
        status=status.HTTP_201_CREATED,
    )

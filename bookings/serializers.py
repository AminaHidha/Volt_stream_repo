from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking

        fields = "__all__"

        read_only_fields = [
            "id",
            "user",
            "booking_status",
            "created_at"
        ]
from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment

        fields = "__all__"

        read_only_fields = [
            "id",
            "user",
            "razorpay_order_id",
            "payment_status",
            "created_at",
        ]

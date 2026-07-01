import razorpay
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from payments.models import Payment

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_payment_service(user, validated_data):

    booking = validated_data["booking"]

    amount = int(float(validated_data["amount"]) * 100)

    razorpay_order = client.order.create(
        {"amount": amount, "currency": "INR", "payment_capture": 1}
    )

    payment = Payment.objects.create(
        user=user,
        booking=booking,
        amount=validated_data["amount"],
        razorpay_order_id=razorpay_order["id"],
    )

    return Response(
        {
            "message": "Payment Order Created",
            "payment_id": payment.id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": amount,
        },
        status=status.HTTP_201_CREATED,
    )


def verify_payment_service(data):

    try:

        payment = Payment.objects.get(razorpay_order_id=data["razorpay_order_id"])

    except Payment.DoesNotExist:

        return Response(
            {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
        )

    payment.payment_status = "paid"
    payment.save()

    return Response({"message": "Payment verified successfully"})

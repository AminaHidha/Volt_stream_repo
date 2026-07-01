from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer
from .services.payment_services import (create_payment_service,
                                        verify_payment_service)


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=PaymentSerializer)
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            return create_payment_service(request.user, serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "razorpay_payment_id": {"type": "string"},
                    "razorpay_order_id": {"type": "string"},
                    "razorpay_signature": {"type": "string"},
                },
            }
        }
    )
    def post(self, request):
        return verify_payment_service(request.data)


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

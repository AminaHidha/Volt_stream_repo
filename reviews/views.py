from django.db.models import Avg
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Review
from .serializers import ReviewSerializer
from .services.review_services import create_review_service


class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ReviewSerializer)
    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            return create_review_service(request.user, serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StationReviewsView(APIView):

    def get(self, request, station_id):
        reviews = Review.objects.filter(station_id=station_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class StationAverageRatingView(APIView):

    def get(self, request, station_id):
        average = Review.objects.filter(station_id=station_id).aggregate(Avg("rating"))
        return Response(
            {"station_id": station_id, "average_rating": average["rating__avg"]}
        )


# ========================
# MY REVIEWS VIEW
# ========================
class MyReviewsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reviews = Review.objects.filter(user=request.user).order_by("-created_at")
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

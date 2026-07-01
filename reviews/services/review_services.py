from rest_framework import status
from rest_framework.response import Response

from reviews.models import Review


def create_review_service(user, validated_data):

    review = Review.objects.create(user=user, **validated_data)

    return Response(
        {"message": "Review added successfully", "review_id": review.id},
        status=status.HTTP_201_CREATED,
    )

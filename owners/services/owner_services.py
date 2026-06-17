from rest_framework.response import Response
from rest_framework import status

from owners.models import OwnerProfile


def create_owner_profile_service(user, validated_data):

    if user.role != "owner":

        return Response(
            {
                "error": "Only owners can create profile"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    if hasattr(user, "owner_profile"):

        return Response(
            {
                "error": "Profile already submitted"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    OwnerProfile.objects.create(
        user=user,
        **validated_data
    )

    return Response(
        {
            "message": "Owner profile submitted",
            "status": "pending"
        },
        status=status.HTTP_201_CREATED
    )
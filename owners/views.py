from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import OwnerProfile
from .serializers import OwnerProfileSerializer
from .services.owner_services import create_owner_profile_service


class OwnerSetupView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OwnerProfileSerializer)
    def post(self, request):
        serializer = OwnerProfileSerializer(data=request.data)
        if serializer.is_valid():
            return create_owner_profile_service(request.user, serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = OwnerProfileSerializer(profile)
        return Response(serializer.data)


class OwnerProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OwnerProfileSerializer)
    def put(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = OwnerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.owner_profile
        except OwnerProfile.DoesNotExist:
            return Response(
                {"error": "Owner profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {
                "business_name": profile.business_name,
                "station_name": profile.station_name,
                "approval_status": profile.approval_status,
                "submitted_at": profile.submitted_at,
            }
        )

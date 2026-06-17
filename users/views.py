from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    VerifyOTPSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ResendOTPSerializer,
    LogoutSerializer
)

from .services.auth_services import (
    login_user_service,
    register_user_service,
    verify_register_otp_service,
    forgot_password_service,
    reset_password_service,
    resend_otp_service,
    google_login_service,
    logout_user_service
)


class RegisterUserView(APIView):

    def post(self, request):

        if getattr(request, 'limited', False):

            return Response(
                {'error': 'Too many registration attempts.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():

            return register_user_service(
                serializer.validated_data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class LoginUserView(APIView):

    def post(self, request):

        if getattr(request, 'limited', False):

            return Response(
                {'error': 'Too many login attempts. Try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            return login_user_service(email, password)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class VerifyOTPView(APIView):

    def post(self, request):

        serializer = VerifyOTPSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            return verify_register_otp_service(email, otp_code)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
 

class ResendOTPView(APIView):

    def post(self, request):

        serializer = ResendOTPSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            purpose = serializer.validated_data['purpose']
            return resend_otp_service(email, purpose)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class ForgotPasswordView(APIView):

    def post(self, request):

        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            return forgot_password_service(email)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordView(APIView):

    def post(self, request):

        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            new_password = serializer.validated_data['new_password']
            return reset_password_service(email, otp_code, new_password)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class GoogleLoginView(APIView):

    def post(self, request):

        token = request.data.get('token')

        return google_login_service(token)
    
class LogoutView(APIView):

    def post(self, request):

        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():

            refresh = serializer.validated_data['refresh']

            return logout_user_service(refresh)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    


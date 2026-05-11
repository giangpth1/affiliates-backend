from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer,
)
from apps.users.services import UserService


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.create(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            display_name=serializer.validated_data['display_name'],
        )

        refresh = RefreshToken()
        refresh['user_id'] = user.id

        return Response({
            'user': user.to_response(),
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )

        refresh = RefreshToken()
        refresh['user_id'] = user.id

        return Response({
            'user': user.to_response(),
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user already contains the authenticated User object
        return Response(request.user.to_response())


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        UserService.change_password(
            user_id=request.user.id,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password'],
        )

        return Response({'detail': 'Đổi mật khẩu thành công.'})

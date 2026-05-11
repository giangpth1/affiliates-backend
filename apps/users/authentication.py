from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from apps.users.services import UserService


class CosmosJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that works with Cosmos DB User model (UUID id).
    """

    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise exceptions.AuthenticationFailed('Token contained no recognizable user identification')

            user = UserService.get_by_id(user_id)
            return user
        except Exception:
            raise exceptions.AuthenticationFailed('User not found')

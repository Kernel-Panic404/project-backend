from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .services import AuthService
from .models import Usuario


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):

        print("========== AUTH ==========")
        print(request.headers)
        print("==========================")

        auth_header = request.headers.get("Authorization")

        print("Authorization:", auth_header)

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        payload = AuthService.validate_token(token)

        if not payload:
            raise AuthenticationFailed("Invalid or expired token.")

        try:
            usuario = Usuario.objects.get(id=payload["user_id"])
        except Usuario.DoesNotExist:
            raise AuthenticationFailed("User not found.")

        if AuthService.is_token_revoked(usuario, token):
            raise AuthenticationFailed("Token revoked.")

        return (usuario, token)
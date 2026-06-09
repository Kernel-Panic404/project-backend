import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, TokenRevocado


class AuthService:
    @staticmethod
    def generate_tokens(usuario):
        refresh = RefreshToken.for_user(usuario)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "usuario": usuario,
        }

    @staticmethod
    def authenticate_user(correo, password):
        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            return None

        if not usuario.activo:
            return None

        if not usuario.verify_password(password):
            return None

        return usuario

    @staticmethod
    def revoke_token(usuario, token):
        TokenRevocado.objects.create(usuario=usuario, token=token)

    @staticmethod
    def is_token_revoked(usuario, token):
        return TokenRevocado.objects.filter(usuario=usuario, token=token).exists()

    @staticmethod
    def validate_token(token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

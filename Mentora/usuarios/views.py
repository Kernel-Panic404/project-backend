from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Usuario
from .serializers import (
    LoginSerializer,
    UsuarioSerializer,
    UsuarioCreacionSerializer,
    TokenSerializer,
)
from .services import AuthService


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.validated_data["usuario"]
            tokens = AuthService.generate_tokens(usuario)
            response_data = {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "usuario": UsuarioSerializer(usuario).data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                AuthService.revoke_token(request.user, refresh_token)
            return Response(
                {"mensaje": "Sesión cerrada correctamente."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class UsuarioCreateView(APIView):
    def post(self, request):
        serializer = UsuarioCreacionSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            response_data = UsuarioSerializer(usuario).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = Usuario.objects.filter(activo=True)
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsuarioDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, usuario_id):
        try:
            usuario = Usuario.objects.get(pk=usuario_id, activo=True)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, usuario_id):
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            if request.user.id != usuario_id and not (request.user.rol and request.user.rol.nombre == "admin"):
                return Response(
                    {"error": "No tiene permisos para actualizar este usuario."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )


class UsuarioDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, usuario_id):
        try:
            if not (request.user.rol and request.user.rol.nombre == "admin"):
                return Response(
                    {"error": "Solo administradores pueden eliminar usuarios."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            usuario = Usuario.objects.get(pk=usuario_id)
            usuario.activo = False
            usuario.save()
            return Response(
                {"mensaje": "Usuario eliminado correctamente."},
                status=status.HTTP_200_OK,
            )
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

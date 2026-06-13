from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Usuario
from .serializers import (
    LoginSerializer,
    UserSerializer,
    UserCreationSerializer,
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
                "user": UserSerializer(usuario).data,
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
                {"message": "Session closed successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class UserCreateView(APIView):
    def post(self, request):
        serializer = UserCreationSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            response_data = UserSerializer(usuario).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = Usuario.objects.filter(activo=True)
        serializer = UserSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            usuario = Usuario.objects.get(pk=user_id, activo=True)
            serializer = UserSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, user_id):
        try:
            usuario = Usuario.objects.get(pk=user_id)
            if request.user.id != user_id and not (request.user.rol and request.user.rol.nombre == "admin"):
                return Response(
                    {"error": "You do not have permission to update this user."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = UserSerializer(usuario, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        try:
            if not (request.user.rol and request.user.rol.nombre == "admin"):
                return Response(
                    {"error": "Only administrators can delete users."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            usuario = Usuario.objects.get(pk=user_id)
            usuario.activo = False
            usuario.save()
            return Response(
                {"message": "User deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Usuario.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

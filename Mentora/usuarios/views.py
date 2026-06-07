"""
Vistas del módulo de usuarios.
Capa controlador: recibe peticiones HTTP y devuelve respuestas JSON.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Usuario, Rol
from .serializers import UsuarioSerializer, RolSerializer


class HolaMundoView(APIView):
    """
    Endpoint de prueba que verifica la conexión a la base de datos
    y la instanciación mínima de una entidad.
    """

    def get(self, request):
        total_usuarios = Usuario.objects.count()
        total_roles = Rol.objects.count()

        respuesta = {
            'mensaje': 'Hola Mundo desde Mentora API',
            'framework': 'Django 4.2 + Django REST Framework',
            'base_de_datos': 'PostgreSQL 15 (conexion activa)',
            'entidades_registradas': {
                'usuarios': total_usuarios,
                'roles': total_roles,
            },
            'estado': 'OK',
        }
        return Response(respuesta, status=status.HTTP_200_OK)


class UsuarioListView(APIView):
    """Lista todos los usuarios activos del sistema."""

    def get(self, request):
        usuarios = Usuario.objects.filter(activo=True)
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioDetailView(APIView):
    """Obtiene, actualiza o elimina un usuario por su ID."""

    def _obtener_usuario(self, usuario_id: int):
        """Busca un usuario por ID o retorna None."""
        try:
            return Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return None

    def get(self, request, usuario_id: int):
        usuario = self._obtener_usuario(usuario_id)
        if usuario is None:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)

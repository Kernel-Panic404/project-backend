from rest_framework import serializers
from .models import Rol, Usuario


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ["id", "nombre"]


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ["id", "nombre", "apellido", "correo", "rol", "activo", "creado_en", "nombre_completo"]

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()

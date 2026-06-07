"""
Serializadores del módulo de usuarios.
Convierten instancias de modelos a JSON y viceversa.
"""
from rest_framework import serializers
from .models import Rol, Usuario, UsuarioRol


class RolSerializer(serializers.ModelSerializer):
    """Serializa la entidad Rol."""

    class Meta:
        model = Rol
        fields = ['id', 'nombre']


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializa la entidad Usuario (sin exponer el hash de contraseña)."""

    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'correo', 'activo', 'creado_en', 'nombre_completo']

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()

from rest_framework import serializers
from .models import Rol, Usuario, Permiso


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ["id", "nombre", "descripcion"]


class RolSerializer(serializers.ModelSerializer):
    permisos = PermisoSerializer(many=True, read_only=True)

    class Meta:
        model = Rol
        fields = ["id", "nombre", "permisos"]


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    rol_display = serializers.CharField(source="get_rol_display", read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "nombre", "apellido", "correo", "rol", "activo", "creado_en", "nombre_completo"]

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        correo = data.get("correo")
        password = data.get("password")
        from .services import AuthService
        usuario = AuthService.authenticate_user(correo, password)
        if not usuario:
            raise serializers.ValidationError("Credenciales inválidas o usuario inactivo.")
        data["usuario"] = usuario
        return data


class UsuarioCreacionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["nombre", "apellido", "correo", "password", "rol"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

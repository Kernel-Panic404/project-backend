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
        fields = [
            "id",
            "nombre",
            "apellido",
            "correo",
            "activo",
            "rol",
            "rol_display",
            "creado_en",
            "nombre_completo",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()


class UsuarioCreacionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ["nombre", "apellido", "correo", "password", "password_confirm", "rol"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        correo = data.get("correo")
        password = data.get("password")

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Credenciales inválidas.")

        if not usuario.activo:
            raise serializers.ValidationError("Usuario inactivo.")

        if not usuario.verify_password(password):
            raise serializers.ValidationError("Credenciales inválidas.")

        data["usuario"] = usuario
        return data


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    usuario = UsuarioSerializer(read_only=True)

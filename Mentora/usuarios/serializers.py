from rest_framework import serializers
from .models import Rol, Usuario, Permiso


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ["id", "nombre", "descripcion"]


class RoleSerializer(serializers.ModelSerializer):
    permisos = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Rol
        fields = ["id", "nombre", "permisos"]


class UserSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    rol_display = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id",
            "nombre",
            "apellido",
            "correo",
            "rol",
            "rol_display",
            "activo",
            "creado_en",
            "actualizado_en",
            "nombre_completo",
        ]

    def get_nombre_completo(self, obj):
        return obj.nombre_completo()

    def get_rol_display(self, obj):
        return obj.rol.nombre if obj.rol else None


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    rol = serializers.CharField()

    def validate(self, data):
        correo = data.get("correo")
        password = data.get("password")
        rol = data.get("rol")

        from .services import AuthService

        usuario = AuthService.authenticate_user(
            correo,
            password,
            rol,
        )

        if not usuario:
            raise serializers.ValidationError(
                "Correo, contraseña o rol incorrectos."
            )

        data["usuario"] = usuario
        return data


class UserCreationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )
    rol = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Usuario
        fields = [
            "nombre",
            "apellido",
            "correo",
            "password",
            "rol",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        # Verificar si quien hace la petición es administrador
        request = self.context.get('request')
        is_admin = False
        if request and request.user and request.user.is_authenticated:
            if request.user.rol and request.user.rol.nombre == "admin":
                is_admin = True

        # Si no es admin, asignamos automáticamente el rol 'estudiante'
        if not is_admin:
            try:
                estudiante_rol = Rol.objects.get(nombre="estudiante")
                validated_data["rol"] = estudiante_rol
            except Rol.DoesNotExist:
                pass

        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()

        return usuario


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

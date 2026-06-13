from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "rol"

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = "permiso"

    def __str__(self):
        return self.nombre


class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name="permisos")
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)

    class Meta:
        db_table = "rol_permiso"
        unique_together = ("rol", "permiso")

    def __str__(self):
        return f"{self.rol.nombre} - {self.permiso.nombre}"


class Usuario(models.Model):
    ROLE_CHOICES = (
        ("estudiante", "Estudiante"),
        ("tutor", "Tutor"),
        ("profesor", "Profesor"),
        ("admin", "Administrador"),
    )

    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido = models.CharField(max_length=100)
    correo = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)

    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    @property
    def is_authenticated(self):
        return True

    class Meta:
        db_table = "usuario"
        indexes = [
            models.Index(fields=["correo"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def esta_activo(self):
        return self.activo

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def verify_password(self, raw_password):
        return check_password(raw_password, self.password_hash)


class TokenRevocado(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "token_revocado"

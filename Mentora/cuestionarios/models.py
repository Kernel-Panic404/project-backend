"""
Modelos del módulo de usuarios.
Representa las entidades: Rol, Usuario y UsuarioRol.
"""
from django.db import models


class Rol(models.Model):
    """Representa un rol dentro del sistema (ej: tutor, estudiante, profesor)."""

    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    """Usuario del sistema Mentora. Puede tener uno o más roles."""

    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido = models.CharField(max_length=100)
    correo = models.CharField(max_length=150)
    password_hash = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.nombre} {self.apellido} <{self.correo}>'

    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario."""
        return f'{self.nombre} {self.apellido}'

    def esta_activo(self) -> bool:
        """Verifica si el usuario está habilitado en el sistema."""
        return self.activo


class UsuarioRol(models.Model):
    """Relación entre un usuario y sus roles asignados."""

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='roles')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        db_table = 'usuario_rol'
        verbose_name = 'Usuario-Rol'
        verbose_name_plural = 'Usuarios-Roles'

    def __str__(self):
        return f'{self.usuario} → {self.rol}'

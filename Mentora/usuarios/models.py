from django.db import models


class Rol(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = "rol"

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido = models.CharField(max_length=100)
    correo = models.CharField(max_length=150)
    password_hash = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuario"

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def esta_activo(self):
        return self.activo

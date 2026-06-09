from django.db import models
from usuarios.models import Usuario


class Tutoria(models.Model):

    estudiante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="tutorias_estudiante"
    )

    tutor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="tutorias_tutor"
    )

    materia = models.CharField(max_length=100)

    fecha = models.DateField()

    hora = models.TimeField()

    estado = models.CharField(
        max_length=20,
        default="PROGRAMADA"
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tutoria"

    def __str__(self):
        return f"{self.materia} - {self.fecha} {self.hora}"
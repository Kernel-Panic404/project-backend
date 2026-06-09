from datetime import date
from .models import Tutoria


class AgendamientoService:

    @staticmethod
    def validar_conflictos(estudiante, tutor, fecha, hora):

        if fecha < date.today():
            raise ValueError(
                "La fecha debe ser futura"
            )

        conflicto_tutor = Tutoria.objects.filter(
            tutor=tutor,
            fecha=fecha,
            hora=hora
        ).exists()

        if conflicto_tutor:
            raise ValueError(
                "El tutor ya tiene una tutoría en ese horario"
            )

        conflicto_estudiante = Tutoria.objects.filter(
            estudiante=estudiante,
            fecha=fecha,
            hora=hora
        ).exists()

        if conflicto_estudiante:
            raise ValueError(
                "El estudiante ya tiene una tutoría en ese horario"
            )
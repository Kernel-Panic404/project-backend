from datetime import datetime
from django.db.models import Q
from django.utils import timezone

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from usuarios.permissions import IsTutor, IsAdmin
from .models import (
    Subject,
    TutorAvailability,
    AvailabilityException,
    TutoringSession,
    TutoringParticipation,
    TutorSubject,
    SessionRecord,
    Attendance,
    Notification,
)


from .serializers import (
    SubjectSerializer,
    TutorAvailabilitySerializer,
    AvailabilityExceptionSerializer,
    TutoringSessionSerializer,
    TutoringParticipationSerializer,
    TutorSubjectSerializer,
    SessionRecordSerializer,
    AttendanceSerializer,
)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class TutorAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = TutorAvailability.objects.all()
    serializer_class = TutorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsTutor | IsAdmin]

    def get_queryset(self):
        if (
            self.request.user.rol
            and self.request.user.rol.nombre.lower() == "admin"
        ):
            return TutorAvailability.objects.all()

        return TutorAvailability.objects.filter(
            tutor=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)



class AvailabilityExceptionViewSet(viewsets.ModelViewSet):
    queryset = AvailabilityException.objects.all()
    serializer_class = AvailabilityExceptionSerializer
    permission_classes = [IsAuthenticated, IsTutor | IsAdmin]

    def get_queryset(self):
        if (
            self.request.user.rol
            and self.request.user.rol.nombre.lower() == "admin"
        ):
            return AvailabilityException.objects.all()

        return AvailabilityException.objects.filter(
            tutor=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)



class TutoringSessionViewSet(viewsets.ModelViewSet):
    queryset = TutoringSession.objects.all()
    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated]

    def _can_manage_session(self, request):
        """
        Solo el tutor o el administrador pueden cancelar
        o reprogramar tutorías.
        """

        if not request.user.rol:
            return False

        return request.user.rol.nombre in [
            "tutor",
            "admin",
        ]

    def perform_create(self, serializer):
        """
        Evita crear tutorías que se crucen en horario
        para el mismo tutor.
        """

        tutor = self.request.user

        fecha = serializer.validated_data["date"]
        hora_inicio = serializer.validated_data["start_time"]
        hora_fin = serializer.validated_data["end_time"]

        conflicto = (
            TutoringSession.objects.filter(
                participacion__user=tutor,
                participacion__role_in_session="tutor",
                date=fecha,
                status="agendada",
            )
            .filter(
                start_time__lt=hora_fin,
                end_time__gt=hora_inicio,
            )
            .exists()
        )

        if conflicto:
            raise ValidationError(
                {
                    "error": "El tutor ya tiene una tutoría programada en ese horario."
                }
            )

        serializer.save()

    def validar_disponibilidad(
        self,
        tutor,
        fecha,
        hora_inicio,
        hora_fin,
        excluir_sesion=None,
    ):
        """
        Valida que el tutor esté disponible para la tutoría.
        """

        fecha_obj = datetime.strptime(
            fecha,
            "%Y-%m-%d",
        ).date()

        hora_inicio_obj = datetime.strptime(
            hora_inicio,
            "%H:%M:%S",
        ).time()

        hora_fin_obj = datetime.strptime(
            hora_fin,
            "%H:%M:%S",
        ).time()

        dia = fecha_obj.weekday()

        disponibilidad = TutorAvailability.objects.filter(
            tutor=tutor,
            day_of_week=dia,
            is_available=True,
            start_time__lte=hora_inicio_obj,
            end_time__gte=hora_fin_obj,
        ).exists()

        if not disponibilidad:
            return "El tutor no tiene disponibilidad ese día u horario."

        excepcion = AvailabilityException.objects.filter(
            tutor=tutor,
            exception_date=fecha_obj,
            is_available=False,
        ).exists()

        if excepcion:
            return "El tutor tiene una excepción de disponibilidad para esa fecha."

        sesiones = TutoringParticipation.objects.filter(
            user=tutor,
            role_in_session="tutor",
        )

        for participacion in sesiones:

            sesion = participacion.session

            if excluir_sesion and sesion.id == excluir_sesion.id:
                continue

            if sesion.date != fecha_obj:
                continue

            if (
                hora_inicio_obj < sesion.end_time
                and hora_fin_obj > sesion.start_time
            ):
                return (
                    "El tutor ya tiene otra tutoría en ese horario."
                )

        return None

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        session = self.get_object()

        if session.status == "cancelada":
            return Response(
                {"error": "La tutoría ya fue cancelada"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if (
            session.cancellation_deadline
            and timezone.now() > session.cancellation_deadline
        ):
            return Response(
                {
                    "error": "Ya pasó el tiempo límite para cancelar la tutoría"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        reason = request.data.get("cancellation_reason")

        if not reason:
            return Response(
                {
                    "error": "Debe indicar un motivo de cancelación"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = "cancelada"
        session.cancellation_reason = reason
        session.save()

        participaciones = TutoringParticipation.objects.filter(session=session)

        for participacion in participaciones:

            Notification.objects.create(
                session=session,
                user=participacion.user,
                channel="sistema",
                sent=False,
                message=(
                    f"La tutoría del {session.date} fue cancelada. "
                    f"Motivo: {reason}"
                ),
            )

        return Response(
            {
                "message": "Tutoría cancelada correctamente"
            }
        )

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        session = self.get_object()

        if session.status == "cancelada":
            return Response(
                {
                    "error": "No se puede reprogramar una tutoría cancelada"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if session.reschedule_count >= 1:
            return Response(
                {
                    "error": "Esta tutoría ya fue reprogramada anteriormente."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        new_date = request.data.get("date")
        new_start_time = request.data.get("start_time")
        new_end_time = request.data.get("end_time")

        if not all([new_date, new_start_time, new_end_time]):
            return Response(
                {
                    "error": "Debe enviar date, start_time y end_time"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Validación de conflicto de horario para el tutor ---
        tutor = TutoringParticipation.objects.filter(
            session=session,
            role_in_session="tutor"
        ).first()

        if tutor:
            conflicto = (
                TutoringSession.objects.filter(
                    participacion__user=tutor.user,
                    participacion__role_in_session="tutor",
                    date=new_date,
                    status="agendada",
                )
                .filter(
                    start_time__lt=new_end_time,
                    end_time__gt=new_start_time,
                )
                .exclude(id=session.id)
                .exists()
            )

            if conflicto:
                return Response(
                    {
                        "error": "El tutor ya tiene otra tutoría en ese horario."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # --- Creación de la nueva sesión ---
        new_session = TutoringSession.objects.create(
            subject=session.subject,
            date=new_date,
            start_time=new_start_time,
            end_time=new_end_time,
            status="agendada",
            rescheduled_from=session,
            reschedule_count=session.reschedule_count + 1,
        )

        participaciones = TutoringParticipation.objects.filter(
            session=session
        )

        for participacion in participaciones:

            TutoringParticipation.objects.create(
                session=new_session,
                user=participacion.user,
                role_in_session=participacion.role_in_session,
            )

            Notification.objects.create(
                session=new_session,
                user=participacion.user,
                channel="sistema",
                sent=False,
                message=(
                    f"Su tutoría fue reprogramada para "
                    f"{new_date} de {new_start_time} a {new_end_time}."
                ),
            )

        session.status = "reprogramada"
        session.save()

        return Response(
            {
                "message": "Tutoría reprogramada correctamente",
                "new_session_id": new_session.id,
            }
        )


class TutoringParticipationViewSet(viewsets.ModelViewSet):
    queryset = TutoringParticipation.objects.all()
    serializer_class = TutoringParticipationSerializer
    permission_classes = [IsAuthenticated]


class TutorSubjectViewSet(viewsets.ModelViewSet):
    queryset = TutorSubject.objects.all()
    serializer_class = TutorSubjectSerializer
    permission_classes = [IsAuthenticated, IsTutor | IsAdmin]


class SessionRecordViewSet(viewsets.ModelViewSet):
    queryset = SessionRecord.objects.all()
    serializer_class = SessionRecordSerializer
    permission_classes = [IsAuthenticated, IsTutor | IsAdmin]


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsTutor | IsAdmin]


class StudentHistoryView(generics.ListAPIView):
    """
    Historial de tutorías de un estudiante.
    """

    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated, IsTutor | IsAdmin]

    def get_queryset(self):
        student_id = self.kwargs.get("student_id")

        participations = TutoringParticipation.objects.filter(
            user_id=student_id,
            role_in_session="estudiante",
        )

        session_ids = participations.values_list(
            "session_id",
            flat=True,
        )

        return TutoringSession.objects.filter(
            id__in=session_ids
        ).order_by(
            "-date",
            "-start_time",
        )
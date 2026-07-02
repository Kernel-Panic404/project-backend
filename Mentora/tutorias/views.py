from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

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
        if self.request.user.rol and self.request.user.rol.nombre == "admin":
            return TutorAvailability.objects.all()
        return TutorAvailability.objects.filter(tutor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)


class AvailabilityExceptionViewSet(viewsets.ModelViewSet):
    queryset = AvailabilityException.objects.all()
    serializer_class = AvailabilityExceptionSerializer
    permission_classes = [IsAuthenticated, IsTutor | IsAdmin]

    def get_queryset(self):
        if self.request.user.rol and self.request.user.rol.nombre == "admin":
            return AvailabilityException.objects.all()
        return AvailabilityException.objects.filter(tutor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)


class TutoringSessionViewSet(viewsets.ModelViewSet):
    queryset = TutoringSession.objects.all()
    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated]

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

        new_session = TutoringSession.objects.create(
            subject=session.subject,
            date=new_date,
            start_time=new_start_time,
            end_time=new_end_time,
            status="agendada",
            rescheduled_from=session,
            reschedule_count=session.reschedule_count + 1
        )

        session.status = "reprogramada"
        session.save()

        return Response(
            {
                "message": "Tutoría reprogramada correctamente",
                "new_session_id": new_session.id
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
    RF-10: View to retrieve tutoring session history for a specific student.
    """
    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated, IsTutor | IsAdmin]

    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        # Find all participations where this user is an 'estudiante'
        participations = TutoringParticipation.objects.filter(user_id=student_id, role_in_session='estudiante')
        session_ids = participations.values_list('session_id', flat=True)
        # Return the corresponding sessions
        return TutoringSession.objects.filter(id__in=session_ids).order_by('-date', '-start_time')

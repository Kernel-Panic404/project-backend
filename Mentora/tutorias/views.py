from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .services import generate_session_reminders

from usuarios.permissions import IsTutor, IsAdmin
from .models import (
    Notification,
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
    NotificationSerializer,
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

class GenerateReminderView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        total = generate_session_reminders()

        return Response({
            "message": "Recordatorios generados",
            "total": total
        })
    
class NotificationListView(generics.ListAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        )
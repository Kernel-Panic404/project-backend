from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from usuarios.permissions import IsTutor, IsAdmin
from .models import (
    Subject,
    TutorAvailability,
    AvailabilityException,
    TutoringSession,
    TutoringParticipation,
    TutorSubject,
)
from .serializers import (
    SubjectSerializer,
    TutorAvailabilitySerializer,
    AvailabilityExceptionSerializer,
    TutoringSessionSerializer,
    TutoringParticipationSerializer,
    TutorSubjectSerializer,
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

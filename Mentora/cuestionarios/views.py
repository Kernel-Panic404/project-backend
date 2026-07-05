from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from usuarios.permissions import IsTutor, IsAdmin

from .models import (
    Questionnaire,
    Question,
    QuestionOption
)

from .serializers import (
    QuestionnaireSerializer,
    QuestionSerializer,
    QuestionOptionSerializer
)


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer

    def get_permissions(self):
        """Cualquiera autenticado puede listar/ver. Solo tutor o admin puede crear/editar/borrar."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), (IsTutor | IsAdmin)()]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), (IsTutor | IsAdmin)()]


class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), (IsTutor | IsAdmin)()]

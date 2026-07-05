from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from usuarios.permissions import IsTutor, IsAdmin

from .models import (
    Questionnaire,
    Question,
    QuestionOption,
    QuestionnaireResult,
    QuestionnaireResponse
)

from .serializers import (
    QuestionnaireSerializer,
    QuestionSerializer,
    QuestionOptionSerializer,
    QuestionnaireResultSerializer,
    QuestionnaireResponseSerializer
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


class QuestionnaireResultViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireResult.objects.all()
    serializer_class = QuestionnaireResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = QuestionnaireResult.objects.all()
        student_id = self.request.query_params.get('student_id')
        questionnaire_id = self.request.query_params.get('questionnaire_id')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if questionnaire_id:
            queryset = queryset.filter(questionnaire_id=questionnaire_id)
            
        return queryset


class QuestionnaireResponseViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireResponse.objects.all()
    serializer_class = QuestionnaireResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = QuestionnaireResponse.objects.all()
        student_id = self.request.query_params.get('student_id')
        questionnaire_id = self.request.query_params.get('questionnaire_id')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if questionnaire_id:
            queryset = queryset.filter(questionnaire_id=questionnaire_id)
            
        return queryset


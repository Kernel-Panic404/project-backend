from rest_framework import viewsets

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


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
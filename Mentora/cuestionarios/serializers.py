from rest_framework import serializers

from .models import (
    Questionnaire,
    Question,
    QuestionOption,
    QuestionnaireResult,
    QuestionnaireResponse
)


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = "__all__"


class QuestionnaireResultSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.nombre_completo')
    questionnaire_title = serializers.ReadOnlyField(source='questionnaire.title')

    class Meta:
        model = QuestionnaireResult
        fields = "__all__"


class QuestionnaireResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireResponse
        fields = "__all__"

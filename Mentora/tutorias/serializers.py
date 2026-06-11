from rest_framework import serializers
from .models import (
    Subject,
    TutorAvailability,
    AvailabilityException,
    TutoringSession,
    TutoringParticipation,
    TutorSubject,
)

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"

class TutorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorAvailability
        fields = "__all__"

class AvailabilityExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityException
        fields = "__all__"

class TutoringSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutoringSession
        fields = "__all__"

class TutoringParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutoringParticipation
        fields = "__all__"

class TutorSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorSubject
        fields = "__all__"

from rest_framework import serializers
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


class SessionRecordSerializer(serializers.ModelSerializer):

    def validate_grade(self, value):

        if value < 1.0 or value > 5.0:
            raise serializers.ValidationError(
                "La calificación debe estar entre 1.0 y 5.0"
            )

        return value

    def validate_observations(self, value):

        if len(value) > 1000:
            raise serializers.ValidationError(
                "La observación no puede superar 1000 caracteres"
            )

        return value

    class Meta:
        model = SessionRecord
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):

    def validate_status(self, value):

        valid_status = [
            "PRESENTE",
            "AUSENTE",
            "TARDE"
        ]

        if value not in valid_status:
            raise serializers.ValidationError(
                "Estado de asistencia inválido"
            )

        return value

    class Meta:
        model = Attendance
        fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"
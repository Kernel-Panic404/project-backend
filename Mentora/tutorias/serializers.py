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
    subject_name = serializers.ReadOnlyField(source='subject.name')
    tutor_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = TutoringSession
        fields = "__all__"

    def get_tutor_name(self, obj):
        part = obj.tutoringparticipation_set.filter(role_in_session='tutor').select_related('user').first()
        if part and part.user:
            return f"{part.user.nombre} {part.user.apellido}"
        return "Tutor no asignado"

    def get_student_name(self, obj):
        part = obj.tutoringparticipation_set.filter(role_in_session='estudiante').select_related('user').first()
        if part and part.user:
            return f"{part.user.nombre} {part.user.apellido}"
        return "Estudiante no asignado"


class TutoringParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutoringParticipation
        fields = "__all__"


class TutorSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorSubject
        fields = "__all__"


class SessionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionRecord
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"

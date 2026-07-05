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

    @action(detail=False, methods=["get"])
    def subject_report(self, request):
        """Returns subjects, showing which tutors teach them and their session counts."""
        subjects = Subject.objects.all()
        results = []
        for s in subjects:
            tutors_data = []
            # Find tutors assigned to this subject
            tutor_subjects = TutorSubject.objects.filter(subject=s).select_related('tutor')
            for ts in tutor_subjects:
                tutor = ts.tutor
                # Count tutoring sessions completed or scheduled by this tutor for this subject
                sessions_count = TutoringSession.objects.filter(
                    subject=s,
                    tutoringparticipation__user=tutor,
                    tutoringparticipation__role_in_session='tutor'
                ).count()
                
                tutors_data.append({
                    "tutor_id": tutor.id,
                    "tutor_name": f"{tutor.nombre} {tutor.apellido}",
                    "sessions_count": sessions_count
                })
            
            results.append({
                "subject_id": s.id,
                "subject_name": s.name,
                "subject_code": s.code,
                "tutors": tutors_data
            })
        return Response(results)


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

    @action(detail=False, methods=["get"])
    def my_tutor_sessions(self, request):
        """Returns sessions where the user is a tutor, including student info."""
        if not request.user.rol or request.user.rol.nombre not in ['tutor', 'admin']:
            return Response({"error": "No permission"}, status=status.HTTP_403_FORBIDDEN)
            
        # Get participations where this user is the tutor
        participations = TutoringParticipation.objects.filter(
            user=request.user, role_in_session='tutor'
        ).select_related('session', 'session__subject')
        
        results = []
        for p in participations:
            session = p.session
            # Find the student participation for this session
            student_part = TutoringParticipation.objects.filter(
                session=session, role_in_session='estudiante'
            ).select_related('user').first()
            
            student_id = student_part.user.id if student_part and student_part.user else None
            student_name = f"{student_part.user.nombre} {student_part.user.apellido}" if student_part and student_part.user else "Desconocido"
            
            results.append({
                "session_id": session.id,
                "date": session.date,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "status": session.status,
                "subject_name": session.subject.name if session.subject else "N/A",
                "student_id": student_id,
                "student_name": student_name
            })
            
        return Response(results)

    @action(detail=False, methods=["get"])
    def tutor_report(self, request):
        """Returns statistics for a tutor (logged in tutor or tutor_id query param) and their students."""
        tutor_id = request.query_params.get('tutor_id')
        if tutor_id:
            try:
                tutor = Usuario.objects.get(pk=tutor_id)
            except Usuario.DoesNotExist:
                return Response({"error": "Tutor not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            tutor = request.user
            if not tutor.rol or tutor.rol.nombre not in ['tutor', 'admin']:
                return Response({"error": "No permission"}, status=status.HTTP_403_FORBIDDEN)

        # Get sessions where this user is the tutor
        participations = TutoringParticipation.objects.filter(
            user=tutor, role_in_session='tutor'
        ).select_related('session')
        
        session_ids = [p.session.id for p in participations]
        
        # Group by student
        student_sessions = {}
        student_parts = TutoringParticipation.objects.filter(
            session_id__in=session_ids, role_in_session='estudiante'
        ).select_related('user', 'session')

        for sp in student_parts:
            student = sp.user
            if student.id not in student_sessions:
                student_sessions[student.id] = {
                    "student_name": f"{student.nombre} {student.apellido}",
                    "student_email": student.correo,
                    "sessions": []
                }
            student_sessions[student.id]["sessions"].append(sp.session)

        results = []
        for s_id, data in student_sessions.items():
            sessions = data["sessions"]
            total_sessions = len(sessions)
            
            # Attendance
            attendances = Attendance.objects.filter(session__in=sessions, user_id=s_id)
            attended_count = attendances.filter(attended=True).count()
            attendance_rate = (attended_count / total_sessions) * 100 if total_sessions > 0 else 0

            # Grades
            records = SessionRecord.objects.filter(session__in=sessions, grade__isnull=False)
            grades = [r.grade for r in records]
            avg_grade = sum(grades) / len(grades) if len(grades) > 0 else None

            results.append({
                "student_id": s_id,
                "student_name": data["student_name"],
                "student_email": data["student_email"],
                "total_sessions": total_sessions,
                "attendance_rate": round(attendance_rate, 2),
                "average_grade": round(float(avg_grade), 2) if avg_grade is not None else None
            })

        return Response({
            "tutor_name": f"{tutor.nombre} {tutor.apellido}",
            "students": results
        })


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

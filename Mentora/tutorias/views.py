from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import date
from django.db.models import Avg, Q


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
                    tutoringparticipation__role_in_session='tutor',
                    status='completada'
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role_name = user.rol.nombre if user.rol else ""
        tutor_id_param = self.request.query_params.get('tutor')

        # Si se pasa ?tutor=ID, filtramos por ese tutor específico
        if tutor_id_param:
            return TutorAvailability.objects.filter(tutor_id=tutor_id_param)

        # Administradores y profesores pueden ver toda la disponibilidad si no hay filtro
        # Estudiantes también deben poder ver la disponibilidad de todos para poder elegirla y agendar
        if role_name in ["admin", "profesor", "estudiante"]:
            return TutorAvailability.objects.all()
        # Los tutores ven su propia disponibilidad
        return TutorAvailability.objects.filter(tutor=user)

    def perform_create(self, serializer):
        user = self.request.user
        role_name = user.rol.nombre if user.rol else ""
        # Solo administrador, profesor o el tutor mismo pueden crear disponibilidad
        if role_name not in ["admin", "profesor", "tutor"]:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permisos para configurar disponibilidad.")
        
        # Si no es admin/profesor, el tutor se asocia automáticamente a sí mismo
        target_tutor = self.request.data.get('tutor') or self.request.data.get('tutor_id')
        if target_tutor and role_name in ["admin", "profesor"]:
            from usuarios.models import Usuario
            tutor_user = Usuario.objects.get(pk=target_tutor)
            serializer.save(tutor=tutor_user)
        else:
            serializer.save(tutor=user)

    def perform_update(self, serializer):
        user = self.request.user
        role_name = user.rol.nombre if user.rol else ""
        if role_name not in ["admin", "profesor"] and serializer.instance.tutor != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permisos para modificar este horario.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        role_name = user.rol.nombre if user.rol else ""
        if role_name not in ["admin", "profesor"] and instance.tutor != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permisos para eliminar este horario.")
        instance.delete()


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

    def create(self, request, *args, **kwargs):
        subject_id = request.data.get('subject_id')
        tutor_id = request.data.get('tutor_id')
        date_str = request.data.get('date')
        start_time_str = request.data.get('start_time')
        end_time_str = request.data.get('end_time')

        if not all([subject_id, tutor_id, date_str, start_time_str, end_time_str]):
            return Response({"error": "Faltan campos obligatorios para agendar la tutoría"}, status=status.HTTP_400_BAD_REQUEST)

        # Validar disponibilidad real del tutor en el día de la semana correspondiente
        from datetime import datetime as dt
        try:
            parsed_date = dt.strptime(date_str, "%Y-%m-%d")
            # En python weekday() va de 0 (Lunes) a 6 (Domingo). 
            # El modelo TutorAvailability va de 1 (Lunes) a 7 (Domingo).
            day_of_week_model = parsed_date.weekday() + 1
        except ValueError:
            return Response({"error": "Formato de fecha inválido"}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar disponibilidad activa
        availability_slot = TutorAvailability.objects.filter(
            tutor_id=tutor_id,
            day_of_week=day_of_week_model,
            start_time__lte=start_time_str,
            end_time__gte=end_time_str,
            is_available=True
        ).first()

        if not availability_slot:
            return Response({"error": "El tutor no está disponible en este día u horario"}, status=status.HTTP_400_BAD_REQUEST)

        # Validar si hay excepciones para ese dia específico (ej. feriado, viaje)
        exception_exists = AvailabilityException.objects.filter(
            tutor_id=tutor_id,
            exception_date=date_str,
            is_available=False
        ).exists()

        if exception_exists:
            return Response({"error": "El tutor ha marcado este día específico como NO disponible por motivos personales/festivos"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si hay una colisión de horario para el mismo tutor en esa fecha
        # (status!='cancelada')
        overlapping_sessions = TutoringSession.objects.filter(
            date=date_str,
            start_time__lt=end_time_str,
            end_time__gt=start_time_str,
            tutoringparticipation__user_id=tutor_id,
            tutoringparticipation__role_in_session='tutor'
        ).exclude(status='cancelada')

        if overlapping_sessions.count() >= availability_slot.max_capacity:
            return Response({"error": "El tutor ya tiene los cupos llenos para este horario"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la tutoría

        session = TutoringSession.objects.create(
            subject_id=subject_id,
            date=date_str,
            start_time=start_time_str,
            end_time=end_time_str,
            status="agendada"
        )

        # Guardar las participaciones del estudiante y del tutor
        # Estudiante es el usuario logueado
        TutoringParticipation.objects.create(
            session=session,
            user=request.user,
            role_in_session='estudiante'
        )

        # Tutor
        from usuarios.models import Usuario as UsuarioModel
        try:
            tutor_user = UsuarioModel.objects.get(pk=tutor_id)
            TutoringParticipation.objects.create(
                session=session,
                user=tutor_user,
                role_in_session='tutor'
            )
        except UsuarioModel.DoesNotExist:
            pass

        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])

    def cancel(self, request, pk=None):
        session = self.get_object()

        if session.status == "cancelada":
            return Response(
                {"error": "La tutoría ya fue cancelada"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Se elimina la comprobación de cancellation_deadline para permitir cancelación libre flexible
        pass

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
            
        # Get participations where role is tutor. If admin/profesor, return all. Otherwise, filter by logged-in tutor.
        is_admin_or_prof = request.user.rol and request.user.rol.nombre in ['admin', 'profesor']
        
        if is_admin_or_prof:
            participations = TutoringParticipation.objects.filter(
                role_in_session='tutor'
            ).select_related('session', 'session__subject')
        else:
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
        from usuarios.models import Usuario as UsuarioModel
        if tutor_id:
            try:
                tutor = UsuarioModel.objects.get(pk=tutor_id)
            except UsuarioModel.DoesNotExist:
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
        
        # Group by student from tutoring sessions
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

            # Grades from session records
            records = SessionRecord.objects.filter(session__in=sessions, grade__isnull=False)
            grades = [r.grade for r in records]
            avg_grade = sum(grades) / len(grades) if len(grades) > 0 else None

            # Questionnaire results for this student linked to this tutor
            from cuestionarios.models import QuestionnaireResult
            q_results = QuestionnaireResult.objects.filter(student_id=s_id, tutor=tutor)
            q_scores = [float(r.total_score) for r in q_results if r.total_score is not None]
            avg_questionnaire_score = round(sum(q_scores) / len(q_scores), 2) if q_scores else None

            results.append({
                "student_id": s_id,
                "student_name": data["student_name"],
                "student_email": data["student_email"],
                "total_sessions": total_sessions,
                "attendance_rate": round(attendance_rate, 2),
                "average_grade": round(float(avg_grade), 2) if avg_grade is not None else None,
                "questionnaire_count": len(q_scores),
                "average_questionnaire_score": avg_questionnaire_score
            })

        # Also include students who responded questionnaires for this tutor but have no sessions
        from cuestionarios.models import QuestionnaireResult
        q_student_ids_with_sessions = set(student_sessions.keys())
        extra_q_results = QuestionnaireResult.objects.filter(
            tutor=tutor
        ).select_related('student').exclude(student_id__in=q_student_ids_with_sessions)

        extra_students = {}
        for qr in extra_q_results:
            student = qr.student
            if student.id not in extra_students:
                extra_students[student.id] = {
                    "student_name": f"{student.nombre} {student.apellido}",
                    "student_email": student.correo,
                    "scores": []
                }
            if qr.total_score is not None:
                extra_students[student.id]["scores"].append(float(qr.total_score))

        for s_id, data in extra_students.items():
            scores = data["scores"]
            avg_q = round(sum(scores) / len(scores), 2) if scores else None
            results.append({
                "student_id": s_id,
                "student_name": data["student_name"],
                "student_email": data["student_email"],
                "total_sessions": 0,
                "attendance_rate": 0,
                "average_grade": None,
                "questionnaire_count": len(scores),
                "average_questionnaire_score": avg_q
            })

        return Response({
            "tutor_name": f"{tutor.nombre} {tutor.apellido}",
            "students": results
        })


class TutoringParticipationViewSet(viewsets.ModelViewSet):
    queryset = TutoringParticipation.objects.all()
    serializer_class = TutoringParticipationSerializer

class TutorSubjectViewSet(viewsets.ModelViewSet):
    queryset = TutorSubject.objects.all()
    serializer_class = TutorSubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tutor_id = self.request.query_params.get('tutor')
        if tutor_id:
            return TutorSubject.objects.filter(tutor_id=tutor_id)
        
        user = self.request.user
        role_name = user.rol.nombre if user.rol else ""
        if role_name in ["admin", "profesor"]:
            return TutorSubject.objects.all()
        elif role_name == "tutor":
            return TutorSubject.objects.filter(tutor=user)
        # Estudiantes pueden ver todas las relaciones de tutor-materia
        return TutorSubject.objects.all()


class SessionRecordViewSet(viewsets.ModelViewSet):
    queryset = SessionRecord.objects.all()
    serializer_class = SessionRecordSerializer
    permission_classes = [IsAuthenticated]


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


class StudentHistoryView(generics.ListAPIView):
    """
    RF-10: View to retrieve tutoring session history for a specific student.
    """
    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_id = self.kwargs.get('student_id')
        # Find all participations where this user is an 'estudiante'
        participations = TutoringParticipation.objects.filter(user_id=student_id, role_in_session='estudiante')
        session_ids = participations.values_list('session_id', flat=True)
        # Return the corresponding sessions
        return TutoringSession.objects.filter(id__in=session_ids).order_by('-date', '-start_time')


class StudentProgressView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        participations = TutoringParticipation.objects.filter(user_id=student_id, role_in_session='estudiante')
        session_ids = participations.values_list('session_id', flat=True)
        sessions = TutoringSession.objects.filter(id__in=session_ids)

        # Count completed sessions strictly by status
        completed_sessions = sessions.filter(status="completada")
        total_completed = completed_sessions.count()

        pending_sessions = sessions.filter(status="agendada").count()

        # Average grade across all completed sessions
        records = SessionRecord.objects.filter(session__in=completed_sessions, grade__isnull=False)
        avg_grade = records.aggregate(Avg('grade'))['grade__avg']
        avg_grade_val = round(float(avg_grade), 2) if avg_grade is not None else None

        # Group by subjects (from tutoring sessions)
        subject_ids = sessions.values_list('subject_id', flat=True).distinct()
        subjects_list = []

        for sub_id in subject_ids:
            if not sub_id:
                continue
            try:
                subject = Subject.objects.get(pk=sub_id)
            except Subject.DoesNotExist:
                continue

            sub_sessions = sessions.filter(subject=subject)
            sub_completed = sub_sessions.filter(status="completada")
            sub_completed_count = sub_completed.count()
            sub_total_count = sub_sessions.count()

            sub_records = SessionRecord.objects.filter(session__in=sub_completed, grade__isnull=False)
            sub_avg = sub_records.aggregate(Avg('grade'))['grade__avg']
            sub_grade_val = round(float(sub_avg), 2) if sub_avg is not None else None

            percentage = int((sub_completed_count / sub_total_count) * 100) if sub_total_count > 0 else 0

            subjects_list.append({
                "id": subject.id,
                "name": subject.name,
                "grade": sub_grade_val,
                "percentage": percentage,
                "sessions_completed": sub_completed_count
            })

        # Questionnaire results for this student
        from cuestionarios.models import QuestionnaireResult
        q_results = QuestionnaireResult.objects.filter(
            student_id=student_id
        ).select_related('questionnaire', 'tutor', 'questionnaire__subject').order_by('-completed_at')

        questionnaire_results = []
        for qr in q_results:
            questionnaire_results.append({
                "id": qr.id,
                "questionnaire_title": qr.questionnaire.title,
                "subject_name": qr.questionnaire.subject.name if qr.questionnaire.subject else None,
                "tutor_name": f"{qr.tutor.nombre} {qr.tutor.apellido}" if qr.tutor else None,
                "total_score": float(qr.total_score) if qr.total_score is not None else None,
                "completed_at": qr.completed_at.strftime("%Y-%m-%d")
            })

        # Average questionnaire score
        q_scores = [r["total_score"] for r in questionnaire_results if r["total_score"] is not None]
        avg_q_score = round(sum(q_scores) / len(q_scores), 2) if q_scores else None

        return Response({
            "average_grade": avg_grade_val,
            "total_sessions": total_completed,
            "pending_sessions": pending_sessions,
            "subjects": subjects_list,
            "questionnaire_results": questionnaire_results,
            "average_questionnaire_score": avg_q_score
        })

from django.db import models
from usuarios.models import Usuario


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "materia"


class TutorAvailability(models.Model):
    tutor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "disponibilidad_tutor"


class AvailabilityException(models.Model):
    tutor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    exception_date = models.DateField()
    is_available = models.BooleanField()
    reason = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "disponibilidad_excepcion"


class TutoringSession(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, default="agendada")
    cancellation_reason = models.TextField(null=True, blank=True)
    rescheduled_from = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    reschedule_count = models.IntegerField(default=0)
    cancellation_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tutoria"


class TutoringParticipation(models.Model):
    session = models.ForeignKey(TutoringSession, on_delete=models.CASCADE)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    role_in_session = models.CharField(max_length=20)

    class Meta:
        db_table = "participacion_tutoria"


class TutorSubject(models.Model):
    tutor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        db_table = "tutor_materia"


class SessionRecord(models.Model):
    session = models.OneToOneField(TutoringSession, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observations = models.TextField(null=True, blank=True)
    topics_covered = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "registro_sesion"


class Attendance(models.Model):
    session = models.ForeignKey(TutoringSession, on_delete=models.CASCADE)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    attended = models.BooleanField()
    observation = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "asistencia"


class Notification(models.Model):
    session = models.ForeignKey(TutoringSession, on_delete=models.CASCADE)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    channel = models.CharField(max_length=20)
    sent = models.BooleanField(default=False)
    send_date = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    send_attempts = models.IntegerField(default=0)
    next_attempt = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "notificacion"

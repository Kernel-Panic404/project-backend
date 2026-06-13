from datetime import timedelta
from django.utils import timezone

from .models import (
    TutoringSession,
    Notification,
    TutoringParticipation
)
def generate_session_reminders():

    tomorrow = timezone.now() + timedelta(hours=24)

    sessions = TutoringSession.objects.filter(
        date=tomorrow.date(),
        status="agendada"
    )

    created = 0

    for session in sessions:

        participants = TutoringParticipation.objects.filter(
            session=session
        )

        for participant in participants:

            Notification.objects.get_or_create(
                session=session,
                user=participant.user,
                channel="APP",
                defaults={
                    "message":
                        f"Recordatorio: tienes una tutoría de "
                        f"{session.subject.name} mañana "
                        f"a las {session.start_time}"
                }
            )

            created += 1

    return created
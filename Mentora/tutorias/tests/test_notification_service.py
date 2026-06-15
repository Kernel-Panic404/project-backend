from unittest.mock import MagicMock
from tutorias.services import generate_session_reminders

class TestNotificationService:

    def test_no_sessions_found(self, mocker):

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[]
        )

        result = generate_session_reminders()

        assert result == 0

    def test_one_session_one_participant(self, mocker):

        session = MagicMock()

        participant = MagicMock()

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[session]
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=[participant]
        )

        mocker.patch(
            "tutorias.services.Notification.objects.get_or_create"
        )

        result = generate_session_reminders()

        assert result == 1

    def test_one_session_many_participants(self, mocker):

        session = MagicMock()

        participants = [
            MagicMock(),
            MagicMock(),
            MagicMock()
        ]

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[session]
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=participants
        )

        mocker.patch(
            "tutorias.services.Notification.objects.get_or_create"
        )

        result = generate_session_reminders()

        assert result == 3

    def test_multiple_sessions(self, mocker):

        sessions = [
            MagicMock(),
            MagicMock()
        ]

        participants = [
            MagicMock(),
            MagicMock()
        ]

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=sessions
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=participants
        )

        mocker.patch(
            "tutorias.services.Notification.objects.get_or_create"
        )

        result = generate_session_reminders()

        assert result == 4

    def test_session_without_participants(self, mocker):

        session = MagicMock()

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[session]
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=[]
        )

        result = generate_session_reminders()

        assert result == 0

    def test_notification_message_contains_subject(self, mocker):

        session = MagicMock()

        session.subject.name = "Matematicas"

        session.start_time = "08:00"

        participant = MagicMock()

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[session]
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=[participant]
        )

        mock_get = mocker.patch(
            "tutorias.services.Notification.objects.get_or_create"
        )

        generate_session_reminders()

        message = mock_get.call_args.kwargs["defaults"]["message"]

        assert "Matematicas" in message

    def test_notification_message_contains_time(self, mocker):

        session = MagicMock()

        session.subject.name = "Fisica"

        session.start_time = "10:00"

        participant = MagicMock()

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[session]
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=[participant]
        )

        mock_get = mocker.patch(
            "tutorias.services.Notification.objects.get_or_create"
        )

        generate_session_reminders()

        message = mock_get.call_args.kwargs["defaults"]["message"]

        assert "10:00" in message

    def test_notification_uses_participant_user(self, mocker):

        session = MagicMock()

        participant = MagicMock()

        participant.user = MagicMock()

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[session]
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=[participant]
        )

        mock_get = mocker.patch(
            "tutorias.services.Notification.objects.get_or_create"
        )

        generate_session_reminders()

        assert (
            mock_get.call_args.kwargs["user"]
            == participant.user
        )
    def test_notification_message_starts_with_recordatorio(self, mocker):

        session = MagicMock()
        session.subject.name = "Programación"
        session.start_time = "14:00"

        participant = MagicMock()

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[session]
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=[participant]
        )

        get_or_create = mocker.patch(
            "tutorias.services.Notification.objects.get_or_create"
        )

        generate_session_reminders()

        _, kwargs = get_or_create.call_args

        message = kwargs["defaults"]["message"]

        assert message.startswith("Recordatorio")
    
    def test_get_or_create_called_once_per_participant(self, mocker):

        session = MagicMock()

        participants = [
            MagicMock(),
            MagicMock(),
            MagicMock()
        ]

        mocker.patch(
            "tutorias.services.TutoringSession.objects.filter",
            return_value=[session]
        )

        mocker.patch(
            "tutorias.services.TutoringParticipation.objects.filter",
            return_value=participants
        )

        mock_get = mocker.patch(
            "tutorias.services.Notification.objects.get_or_create"
        )

        generate_session_reminders()

        assert mock_get.call_count == 3
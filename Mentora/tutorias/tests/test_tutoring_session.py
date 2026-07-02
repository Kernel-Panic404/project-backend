from unittest.mock import MagicMock, patch
from rest_framework.test import APIRequestFactory

from tutorias.views import TutoringSessionViewSet


def test_cancel_already_cancelled_session_returns_error():

    factory = APIRequestFactory()

    request = factory.post(
        "/cancel/",
        {"cancellation_reason": "No asistiré"},
        format="json"
    )

    request.data = {
        "cancellation_reason": "No asistiré"
    }

    view = TutoringSessionViewSet()

    session = MagicMock()
    session.status = "cancelada"

    view.get_object = MagicMock(return_value=session)

    response = view.cancel(request)

    assert response.status_code == 400
    assert response.data == {
        "error": "La tutoría ya fue cancelada"
    }


def test_cancel_session_without_reason_returns_error():

    factory = APIRequestFactory()

    request = factory.post(
        "/cancel/",
        {},
        format="json"
    )

    request.data = {}

    view = TutoringSessionViewSet()

    session = MagicMock()
    session.status = "agendada"
    session.cancellation_deadline = None

    view.get_object = MagicMock(return_value=session)

    response = view.cancel(request)

    assert response.status_code == 400
    assert response.data == {
        "error": "Debe indicar un motivo de cancelación"
    }


@patch("tutorias.views.TutoringSession.objects.create")
def test_reschedule_session_successfully(mock_create):

    factory = APIRequestFactory()

    request = factory.post(
        "/reschedule/",
        {
            "date": "2026-08-01",
            "start_time": "08:00",
            "end_time": "10:00"
        },
        format="json"
    )

    request.data = {
        "date": "2026-08-01",
        "start_time": "08:00",
        "end_time": "10:00"
    }

    view = TutoringSessionViewSet()

    session = MagicMock()
    session.status = "agendada"
    session.subject = MagicMock()
    session.reschedule_count = 0

    view.get_object = MagicMock(return_value=session)

    new_session = MagicMock()
    new_session.id = 15

    mock_create.return_value = new_session

    response = view.reschedule(request)

    assert response.status_code == 200

    assert response.data == {
        "message": "Tutoría reprogramada correctamente",
        "new_session_id": 15
    }

    session.save.assert_called_once()
    assert session.status == "reprogramada"

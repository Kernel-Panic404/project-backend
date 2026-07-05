import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestTutoringSessions:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def setup_data(self):
        from usuarios.models import Rol, Usuario
        from tutorias.models import Subject, TutoringSession
        
        rol_tutor = Rol.objects.create(nombre='tutor')
        rol_estudiante = Rol.objects.create(nombre='estudiante')
        
        tutor = Usuario(
            correo='tutor@example.com',
            nombre='Test',
            apellido='Tutor',
            rol=rol_tutor
        )
        tutor.set_password('password123')
        tutor.save()
        
        student = Usuario(
            correo='student@example.com',
            nombre='Test',
            apellido='Student',
            rol=rol_estudiante
        )
        student.set_password('password123')
        student.save()
        
        subject = Subject.objects.create(name='Matematicas', code='MAT101')
        
        session = TutoringSession.objects.create(
            subject=subject,
            date='2025-01-01',
            start_time='10:00:00',
            end_time='11:00:00',
            status='agendada'
        )
        
        return {
            'tutor': tutor,
            'student': student,
            'subject': subject,
            'session': session
        }

    def test_cancel_session_success(self, client, setup_data):
        client.force_authenticate(user=setup_data['student'])
        url = reverse('tutoringsession-cancel', kwargs={'pk': setup_data['session'].id})
        
        data = {'cancellation_reason': 'No puedo asistir'}
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify db updated
        setup_data['session'].refresh_from_db()
        assert setup_data['session'].status == 'cancelada'
        assert setup_data['session'].cancellation_reason == 'No puedo asistir'

    def test_cancel_session_missing_reason(self, client, setup_data):
        client.force_authenticate(user=setup_data['student'])
        url = reverse('tutoringsession-cancel', kwargs={'pk': setup_data['session'].id})
        
        data = {}
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reschedule_session_success(self, client, setup_data):
        client.force_authenticate(user=setup_data['student'])
        url = reverse('tutoringsession-reschedule', kwargs={'pk': setup_data['session'].id})
        
        data = {
            'date': '2025-01-02',
            'start_time': '12:00:00',
            'end_time': '13:00:00'
        }
        
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'new_session_id' in response.data
        
        # Verify old session
        setup_data['session'].refresh_from_db()
        assert setup_data['session'].status == 'reprogramada'
        
        # Verify new session
        from tutorias.models import TutoringSession
        new_session = TutoringSession.objects.get(id=response.data['new_session_id'])
        assert new_session.status == 'agendada'
        assert new_session.date.strftime('%Y-%m-%d') == '2025-01-02'
        assert new_session.rescheduled_from == setup_data['session']
        assert new_session.reschedule_count == 1

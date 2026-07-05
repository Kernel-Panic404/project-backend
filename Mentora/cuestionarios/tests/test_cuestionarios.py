import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestCuestionarios:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def setup_data(self):
        from usuarios.models import Rol, Usuario
        from tutorias.models import Subject
        from cuestionarios.models import Questionnaire, Question, QuestionOption
        
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
        
        subject = Subject.objects.create(name='Física', code='FIS101')
        
        questionnaire = Questionnaire.objects.create(
            title='Prueba 1',
            teacher=tutor,
            subject=subject
        )
        
        q1 = Question.objects.create(
            questionnaire=questionnaire,
            statement='¿2 + 2?',
            question_type='multiple_choice',
            max_score=5.0
        )
        
        q1_opt1 = QuestionOption.objects.create(question=q1, text='4', is_correct=True)
        q1_opt2 = QuestionOption.objects.create(question=q1, text='5', is_correct=False)
        
        q2 = Question.objects.create(
            questionnaire=questionnaire,
            statement='¿Verdadero o falso?',
            question_type='boolean',
            max_score=5.0
        )
        
        return {
            'tutor': tutor,
            'student': student,
            'subject': subject,
            'questionnaire': questionnaire,
            'q1': q1,
            'q1_opt1': q1_opt1,
            'q1_opt2': q1_opt2,
            'q2': q2
        }

    def test_submit_questionnaire_success(self, client, setup_data):
        client.force_authenticate(user=setup_data['student'])
        url = reverse('questionnaire-submit')
        
        data = {
            'questionnaire_id': setup_data['questionnaire'].id,
            'answers': {
                str(setup_data['q1'].id): str(setup_data['q1_opt1'].id), # Correct multiple choice
                str(setup_data['q2'].id): True # Let's assume True is correct for now (though boolean just takes points if true, wait)
            }
        }
        
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'total_score' in response.data
        
        # Verify db records
        from cuestionarios.models import QuestionnaireResult, QuestionnaireResponse
        result = QuestionnaireResult.objects.get(questionnaire=setup_data['questionnaire'], student=setup_data['student'])
        
        # Since q2 boolean is True but has no correct option defined, it gives 0.0, q1 correct option gives 5.0 -> Total 5.0
        assert float(result.total_score) == 5.0
        
        responses = QuestionnaireResponse.objects.filter(questionnaire=setup_data['questionnaire'])
        assert responses.count() == 2

    def test_submit_questionnaire_not_found(self, client, setup_data):
        client.force_authenticate(user=setup_data['student'])
        url = reverse('questionnaire-submit')
        
        data = {
            'questionnaire_id': 999,
            'answers': {}
        }
        
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

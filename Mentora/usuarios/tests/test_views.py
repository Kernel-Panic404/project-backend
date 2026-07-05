import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch


@pytest.mark.django_db
class TestLoginView:
    @pytest.fixture
    def client(self):
        return APIClient()

    @patch('usuarios.views.AuthService.generate_tokens')
    def test_login_success(self, mock_generate, client):
        from usuarios.models import Rol, Usuario
        rol = Rol.objects.create(nombre='estudiante')
        user = Usuario(
            correo='test@example.com',
            nombre='Test',
            apellido='User',
            rol=rol
        )
        user.set_password('password123')
        user.save()
        
        mock_generate.return_value = {
            "access": "mock_access_token",
            "refresh": "mock_refresh_token"
        }

        url = reverse('login')
        data = {
            'correo': 'test@example.com',
            'password': 'password123',
            'rol': 'estudiante'
        }
        
        # We need to mock AuthService.authenticate_user because LoginSerializer uses it
        with patch('usuarios.services.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = user
            response = client.post(url, data)
            
            assert response.status_code == status.HTTP_200_OK
            assert 'access' in response.data
            assert response.data['access'] == 'mock_access_token'

    def test_login_invalid_credentials(self, client):
        url = reverse('login')
        data = {
            'correo': 'wrong@example.com',
            'password': 'wrongpassword',
            'rol': 'estudiante'
        }
        
        with patch('usuarios.services.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            response = client.post(url, data)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutView:
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_logout_success(self, client):
        from usuarios.models import Rol, Usuario
        rol = Rol.objects.create(nombre='estudiante')
        user = Usuario(
            correo='test@example.com',
            nombre='Test',
            apellido='User',
            rol=rol
        )
        user.set_password('password123')
        user.save()
        client.force_authenticate(user=user)
        
        url = reverse('logout')
        data = {'refresh': 'fake_refresh_token'}
        
        with patch('usuarios.views.AuthService.revoke_token') as mock_revoke:
            response = client.post(url, data)
            
            assert response.status_code == status.HTTP_200_OK
            mock_revoke.assert_called_once_with(user, 'fake_refresh_token')

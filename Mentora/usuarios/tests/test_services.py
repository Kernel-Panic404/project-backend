import pytest
import jwt
from unittest.mock import MagicMock
from usuarios.services import AuthService
from usuarios.models import Usuario

class TestAuthService:
    def test_authenticate_user_success(self, mocker):
        # Configurar el mock
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = True
        mock_user.verify_password.return_value = True

        mocker.patch('usuarios.models.Usuario.objects.get', return_value=mock_user)

        # Ejecutar
        result = AuthService.authenticate_user('test@test.com', 'password123')

        # Verificar
        assert result == mock_user
        mock_user.verify_password.assert_called_once_with('password123')

    def test_authenticate_user_invalid_password(self, mocker):
        # Configurar el mock
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = True
        mock_user.verify_password.return_value = False

        mocker.patch('usuarios.models.Usuario.objects.get', return_value=mock_user)

        # Ejecutar
        result = AuthService.authenticate_user('test@test.com', 'wrongpass')

        # Verificar
        assert result is None

    def test_authenticate_user_inactive(self, mocker):
        # Configurar el mock
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = False

        mocker.patch('usuarios.models.Usuario.objects.get', return_value=mock_user)

        # Ejecutar
        result = AuthService.authenticate_user('test@test.com', 'password123')

        # Verificar
        assert result is None
        # La contraseña no debería verificarse si está inactivo
        mock_user.verify_password.assert_not_called()

    def test_authenticate_user_not_found(self, mocker):
        # Configurar el mock para que levante excepcion
        mocker.patch('usuarios.models.Usuario.objects.get', side_effect=Usuario.DoesNotExist)

        # Ejecutar
        result = AuthService.authenticate_user('unknown@test.com', 'password123')

        # Verificar
        assert result is None

    def test_validate_token_success(self, mocker):
        # Configurar el mock de jwt.decode
        expected_payload = {'user_id': 1, 'email': 'test@test.com'}
        mocker.patch('jwt.decode', return_value=expected_payload)

        # Ejecutar
        result = AuthService.validate_token('valid.token.here')

        # Verificar
        assert result == expected_payload

    def test_validate_token_expired(self, mocker):
        # Configurar el mock para que simule token expirado
        mocker.patch('jwt.decode', side_effect=jwt.ExpiredSignatureError)

        # Ejecutar
        result = AuthService.validate_token('expired.token.here')

        # Verificar
        assert result is None

    def test_validate_token_invalid(self, mocker):
        # Configurar el mock para que simule token invalido
        mocker.patch('jwt.decode', side_effect=jwt.InvalidTokenError)

        # Ejecutar
        result = AuthService.validate_token('invalid.token.here')

        # Verificar
        assert result is None

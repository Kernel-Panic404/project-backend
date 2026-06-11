import pytest
import jwt
from unittest.mock import MagicMock
from usuarios.services import AuthService
from usuarios.models import Usuario

class TestAuthService:
    def test_authenticate_user_success(self, mocker):
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = True
        mock_user.verify_password.return_value = True

        mocker.patch('usuarios.models.Usuario.objects.get', return_value=mock_user)

        result = AuthService.authenticate_user('test@test.com', 'password123')

        assert result == mock_user
        mock_user.verify_password.assert_called_once_with('password123')

    def test_authenticate_user_invalid_password(self, mocker):
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = True
        mock_user.verify_password.return_value = False

        mocker.patch('usuarios.models.Usuario.objects.get', return_value=mock_user)

        result = AuthService.authenticate_user('test@test.com', 'wrongpass')

        assert result is None

    def test_authenticate_user_inactive(self, mocker):
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = False

        mocker.patch('usuarios.models.Usuario.objects.get', return_value=mock_user)

        result = AuthService.authenticate_user('test@test.com', 'password123')

        assert result is None
        mock_user.verify_password.assert_not_called()

    def test_authenticate_user_not_found(self, mocker):
        mocker.patch('usuarios.models.Usuario.objects.get', side_effect=Usuario.DoesNotExist)

        result = AuthService.authenticate_user('unknown@test.com', 'password123')

        assert result is None

    def test_validate_token_success(self, mocker):
        expected_payload = {'user_id': 1, 'email': 'test@test.com'}
        mocker.patch('jwt.decode', return_value=expected_payload)

        result = AuthService.validate_token('valid.token.here')

        assert result == expected_payload

    def test_validate_token_expired(self, mocker):
        mocker.patch('jwt.decode', side_effect=jwt.ExpiredSignatureError)

        result = AuthService.validate_token('expired.token.here')

        assert result is None

    def test_validate_token_invalid(self, mocker):
        mocker.patch('jwt.decode', side_effect=jwt.InvalidTokenError)

        result = AuthService.validate_token('invalid.token.here')

        assert result is None

import jwt
from unittest.mock import MagicMock
from usuarios.services import AuthService
from usuarios.models import Usuario


class TestAuthService:
    def test_authenticate_user_success(self, mocker):
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = True
        mock_user.verify_password.return_value = True
        mock_user.rol.nombre = 'estudiante'

        mock_qs = MagicMock()
        mock_qs.get.return_value = mock_user
        mocker.patch('usuarios.models.Usuario.objects.select_related', return_value=mock_qs)

        result = AuthService.authenticate_user('test@test.com', 'password123', 'estudiante')

        assert result == mock_user
        mock_user.verify_password.assert_called_once_with('password123')

    def test_authenticate_user_invalid_password(self, mocker):
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = True
        mock_user.verify_password.return_value = False
        mock_user.rol.nombre = 'estudiante'

        mock_qs = MagicMock()
        mock_qs.get.return_value = mock_user
        mocker.patch('usuarios.models.Usuario.objects.select_related', return_value=mock_qs)

        result = AuthService.authenticate_user('test@test.com', 'wrongpass', 'estudiante')

        assert result is None

    def test_authenticate_user_inactive(self, mocker):
        mock_user = MagicMock(spec=Usuario)
        mock_user.activo = False
        mock_user.rol.nombre = 'estudiante'

        mock_qs = MagicMock()
        mock_qs.get.return_value = mock_user
        mocker.patch('usuarios.models.Usuario.objects.select_related', return_value=mock_qs)

        result = AuthService.authenticate_user('test@test.com', 'password123', 'estudiante')

        assert result is None
        mock_user.verify_password.assert_not_called()

    def test_authenticate_user_not_found(self, mocker):
        mock_qs = MagicMock()
        mock_qs.get.side_effect = Usuario.DoesNotExist
        mocker.patch('usuarios.models.Usuario.objects.select_related', return_value=mock_qs)

        result = AuthService.authenticate_user('unknown@test.com', 'password123', 'estudiante')

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

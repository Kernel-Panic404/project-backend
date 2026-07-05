import pytest
from unittest.mock import MagicMock
from usuarios.permissions import IsEstudiante, IsTutor, IsProfesor, IsAdmin

class TestPermissions:
    @pytest.fixture
    def mock_request(self):
        request = MagicMock()
        request.user.is_authenticated = True
        return request

    def test_is_estudiante(self, mock_request):
        mock_request.user.rol.nombre = "estudiante"
        permission = IsEstudiante()
        assert permission.has_permission(mock_request, None) is True
        
        mock_request.user.rol.nombre = "tutor"
        assert permission.has_permission(mock_request, None) is False

    def test_is_tutor(self, mock_request):
        mock_request.user.rol.nombre = "tutor"
        permission = IsTutor()
        assert permission.has_permission(mock_request, None) is True
        
        mock_request.user.rol.nombre = "estudiante"
        assert permission.has_permission(mock_request, None) is False

    def test_is_profesor(self, mock_request):
        mock_request.user.rol.nombre = "profesor"
        permission = IsProfesor()
        assert permission.has_permission(mock_request, None) is True
        
        mock_request.user.rol.nombre = "estudiante"
        assert permission.has_permission(mock_request, None) is False

    def test_is_admin(self, mock_request):
        mock_request.user.rol.nombre = "admin"
        permission = IsAdmin()
        assert permission.has_permission(mock_request, None) is True
        
        mock_request.user.rol.nombre = "tutor"
        assert permission.has_permission(mock_request, None) is False

    def test_unauthenticated_user(self):
        request = MagicMock()
        request.user.is_authenticated = False
        
        permission = IsEstudiante()
        assert permission.has_permission(request, None) is False

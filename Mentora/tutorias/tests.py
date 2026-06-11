from django.test import TestCase
from usuarios.models import Rol, Usuario

class RolModelTest(TestCase):
    def test_create_role(self):
        rol = Rol.objects.create(nombre='estudiante')
        self.assertEqual(str(rol), 'estudiante')

    def test_role_name(self):
        rol = Rol.objects.create(nombre='tutor')
        self.assertEqual(rol.nombre, 'tutor')

class UserModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nombre='Carlos',
            apellido='Gomez',
            correo='carlos@unal.edu.co',
            password_hash='hash_seguro',
        )

    def test_full_name(self):
        self.assertEqual(self.usuario.nombre_completo(), 'Carlos Gomez')

    def test_user_active_by_default(self):
        self.assertTrue(self.usuario.esta_activo())

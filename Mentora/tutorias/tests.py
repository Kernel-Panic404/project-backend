"""
Pruebas básicas del módulo de usuarios.
"""
from django.test import TestCase
from .models import Rol, Usuario


class RolModelTest(TestCase):
    """Pruebas del modelo Rol."""

    def test_crear_rol(self):
        rol = Rol.objects.create(nombre='estudiante')
        self.assertEqual(str(rol), 'estudiante')

    def test_nombre_rol(self):
        rol = Rol.objects.create(nombre='tutor')
        self.assertEqual(rol.nombre, 'tutor')


class UsuarioModelTest(TestCase):
    """Pruebas del modelo Usuario."""

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nombre='Carlos',
            apellido='Gómez',
            correo='carlos@unal.edu.co',
            password_hash='hash_seguro',
        )

    def test_nombre_completo(self):
        self.assertEqual(self.usuario.nombre_completo(), 'Carlos Gómez')

    def test_usuario_activo_por_defecto(self):
        self.assertTrue(self.usuario.esta_activo())

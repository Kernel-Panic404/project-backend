import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario, Rol
from tutorias.models import Subject
from django.contrib.auth.hashers import make_password

def seed():
    # 1. Create a Tutor Role if it doesn't exist
    rol_tutor, created = Rol.objects.get_or_create(nombre='tutor', defaults={'descripcion': 'Tutor del sistema'})
    
    # 2. Create a Test Tutor user
    tutor_email = 'tutor@mentora.com'
    if not Usuario.objects.filter(correo=tutor_email).exists():
        tutor = Usuario.objects.create(
            correo=tutor_email,
            nombre='Profesor',
            apellido='Prueba',
            password_hash=make_password('password123'),
            rol=rol_tutor,
            activo=True
        )
        print(f"Created tutor: {tutor.nombre} {tutor.apellido} (Email: {tutor_email})")
    else:
        print("Tutor user already exists.")

    # 3. Create some basic Subjects
    subjects_data = [
        {"name": "Cálculo Diferencial", "code": "MAT-101", "description": "Límites, derivadas y aplicaciones"},
        {"name": "Física Mecánica", "code": "FIS-101", "description": "Cinemática, dinámica y leyes de Newton"},
        {"name": "Programación Orientada a Objetos", "code": "ING-201", "description": "Java, Python y conceptos OOP"}
    ]

    for data in subjects_data:
        subject, created = Subject.objects.get_or_create(code=data['code'], defaults={
            'name': data['name'],
            'description': data['description']
        })
        if created:
            print(f"Created subject: {subject.name}")
        else:
            print(f"Subject already exists: {subject.name}")

if __name__ == '__main__':
    seed()
    print("Seed completed.")

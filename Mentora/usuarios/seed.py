import os
from datetime import date, datetime, timedelta, time
from django.conf import settings
from django.contrib.auth.hashers import make_password
from usuarios.models import Rol, Usuario
from tutorias.models import (
    Subject,
    TutorAvailability,
    TutorSubject,
    TutoringSession,
    TutoringParticipation,
)
from cuestionarios.models import (
    Questionnaire,
    Question,
    QuestionOption,
)

def download_dummy_image(filename, url):
    """Downloads a placeholder image for testing if it doesn't exist."""
    media_dir = os.path.join(settings.MEDIA_ROOT, 'questions')
    os.makedirs(media_dir, exist_ok=True)
    image_path = os.path.join(media_dir, filename)
    if not os.path.exists(image_path):
        try:
            import urllib.request
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                with open(image_path, 'wb') as f:
                    f.write(response.read())
        except Exception as e:
            # Fallback to a tiny 1x1 transparent PNG
            tiny_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
            with open(image_path, 'wb') as f:
                f.write(tiny_png)

# ============================================================
# ROLES
# ============================================================
def create_roles(command):
    roles = ["admin", "profesor", "tutor", "estudiante"]
    command.stdout.write("Creando roles...")
    for nombre in roles:
        _, created = Rol.objects.get_or_create(nombre=nombre)
        if created:
            command.stdout.write(command.style.SUCCESS(f"   ✓ Rol: {nombre}"))
        else:
            command.stdout.write(command.style.WARNING(f"   • Rol {nombre} ya existe"))

# ============================================================
# USUARIOS
# ============================================================
def create_users(command):
    command.stdout.write("\nCreando usuarios...")
    users = [
        # Admins
        {"nombre": "Administrador", "apellido": "Sistema", "correo": "admin@mentora.com", "password": "Admin123", "rol": "admin"},
        # Profesores
        {"nombre": "Profesor", "apellido": "Demo", "correo": "profesor@mentora.com", "password": "Profesor123", "rol": "profesor"},
        # Tutores
        {"nombre": "Tutor", "apellido": "Demo", "correo": "tutor@mentora.com", "password": "Tutor123", "rol": "tutor"},
        {"nombre": "Ana", "apellido": "Gómez (Tutor)", "correo": "ana.tutor@mentora.com", "password": "Tutor123", "rol": "tutor"},
        {"nombre": "Carlos", "apellido": "Ruiz (Tutor)", "correo": "carlos.tutor@mentora.com", "password": "Tutor123", "rol": "tutor"},
        # Estudiantes
        {"nombre": "Estudiante", "apellido": "Demo", "correo": "estudiante@mentora.com", "password": "Estudiante123", "rol": "estudiante"},
        {"nombre": "Laura", "apellido": "Martínez (Estudiante)", "correo": "laura.estudiante@mentora.com", "password": "Estudiante123", "rol": "estudiante"},
        {"nombre": "Juan", "apellido": "Pérez (Estudiante)", "correo": "juan.estudiante@mentora.com", "password": "Estudiante123", "rol": "estudiante"},
    ]

    for data in users:
        rol = Rol.objects.get(nombre=data["rol"])
        usuario, created = Usuario.objects.get_or_create(
            correo=data["correo"],
            defaults={
                "nombre": data["nombre"],
                "apellido": data["apellido"],
                "rol": rol,
                "activo": True
            }
        )
        if created:
            usuario.set_password(data["password"])
            usuario.save()
            command.stdout.write(command.style.SUCCESS(f"   ✓ Usuario: {usuario.correo}"))
        else:
            usuario.nombre = data["nombre"]
            usuario.apellido = data["apellido"]
            usuario.rol = rol
            usuario.set_password(data["password"])
            usuario.save()
            command.stdout.write(command.style.WARNING(f"   • Usuario {usuario.correo} actualizado"))

# ============================================================
# MATERIAS
# ============================================================
def create_subjects(command):
    command.stdout.write("\nCreando materias...")
    subjects = [
        ("Programación I", "PRG101", "Introducción a programación"),
        ("Bases de Datos", "BD201", "Modelo relacional y SQL"),
        ("Álgebra Lineal", "ALG101", "Matrices y vectores"),
        ("Cálculo I", "CAL101", "Límites y derivadas"),
        ("Física I", "FIS101", "Mecánica clásica"),
    ]
    for name, code, description in subjects:
        _, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "description": description,
            }
        )
        if created:
            command.stdout.write(command.style.SUCCESS(f"   ✓ Materia: {name}"))
        else:
            command.stdout.write(command.style.WARNING(f"   • Materia {name} ya existe"))

# ============================================================
# TUTOR - MATERIAS
# ============================================================
def create_tutor_subjects(command):
    command.stdout.write("\nAsignando materias a los tutores...")
    tutores = Usuario.objects.filter(rol__nombre="tutor")
    materias = Subject.objects.all()

    for tutor in tutores:
        for materia in materias:
            _, created = TutorSubject.objects.get_or_create(tutor=tutor, subject=materia)
            if created:
                command.stdout.write(command.style.SUCCESS(f"   ✓ Materia {materia.name} -> {tutor.nombre}"))

# ============================================================
# DISPONIBILIDAD
# ============================================================
def create_availability(command):
    command.stdout.write("\nCreando disponibilidad...")
    tutores = Usuario.objects.filter(rol__nombre="tutor")
    schedules = [
        (1, time(8, 0), time(10, 0)),
        (2, time(10, 0), time(12, 0)),
        (3, time(14, 0), time(16, 0)),
        (4, time(8, 0), time(10, 0)),
        (5, time(10, 0), time(12, 0)),
    ]

    for tutor in tutores:
        for day, start, end in schedules:
            _, created = TutorAvailability.objects.get_or_create(
                tutor=tutor,
                day_of_week=day,
                start_time=start,
                end_time=end,
                defaults={"is_available": True}
            )
            if created:
                command.stdout.write(command.style.SUCCESS(f"   ✓ Disp. Día {day} -> {tutor.nombre}"))

# ============================================================
# TUTORÍAS (FUTURAS Y PASADAS)
# ============================================================
def create_sessions(command):
    command.stdout.write("\nCreando tutorías de prueba...")
    materias = list(Subject.objects.all().order_by("id"))
    if not materias:
        return

    # Creamos tanto tutorías futuras como tutorías pasadas (para probar post-tutorías)
    sessions = [
        # Pasadas (para evaluación post-tutoría)
        {
            "subject": materias[0],
            "date": date.today() - timedelta(days=2),
            "start": time(8, 0),
            "end": time(10, 0),
            "status": "agendada", # Todavía agendada para poder evaluarla
        },
        {
            "subject": materias[1],
            "date": date.today() - timedelta(days=1),
            "start": time(10, 0),
            "end": time(12, 0),
            "status": "agendada",
        },
        # Futuras
        {
            "subject": materias[2],
            "date": date.today() + timedelta(days=2),
            "start": time(8, 0),
            "end": time(10, 0),
            "status": "agendada",
        },
        {
            "subject": materias[3],
            "date": date.today() + timedelta(days=3),
            "start": time(10, 0),
            "end": time(12, 0),
            "status": "agendada",
        },
    ]

    for data in sessions:
        session, created = TutoringSession.objects.get_or_create(
            subject=data["subject"],
            date=data["date"],
            start_time=data["start"],
            end_time=data["end"],
            defaults={
                "status": data["status"],
                "cancellation_deadline": datetime.combine(data["date"], data["start"]) - timedelta(hours=24),
                "reschedule_count": 0,
            }
        )
        if created:
            command.stdout.write(command.style.SUCCESS(f"   ✓ Tutoría {data['subject'].name} ({data['date']})"))

# ============================================================
# PARTICIPANTES
# ============================================================
def create_participations(command):
    command.stdout.write("\nAsignando participantes...")
    tutores = list(Usuario.objects.filter(rol__nombre="tutor"))
    estudiantes = list(Usuario.objects.filter(rol__nombre="estudiante"))
    sesiones = TutoringSession.objects.all()

    for idx, session in enumerate(sesiones):
        tutor = tutores[idx % len(tutores)]
        estudiante = estudiantes[idx % len(estudiantes)]

        # Asignar Tutor
        _, created_tutor = TutoringParticipation.objects.get_or_create(
            session=session,
            user=tutor,
            defaults={"role_in_session": "tutor"}
        )
        if created_tutor:
            command.stdout.write(command.style.SUCCESS(f"   ✓ Tutor: {tutor.nombre} -> Tutoría {session.id}"))

        # Asignar Estudiante
        _, created_estudiante = TutoringParticipation.objects.get_or_create(
            session=session,
            user=estudiante,
            defaults={"role_in_session": "estudiante"}
        )
        if created_estudiante:
            command.stdout.write(command.style.SUCCESS(f"   ✓ Estudiante: {estudiante.nombre} -> Tutoría {session.id}"))

# ============================================================
# CUESTIONARIOS CON IMÁGENES
# ============================================================
def create_questionnaires(command):
    command.stdout.write("\nCreando cuestionarios de prueba con imágenes...")
    
    # Descargar imágenes de prueba en la carpeta media del backend
    download_dummy_image("math.png", "https://fastly.picsum.photos/id/1010/400/300.jpg?hmac=n_F0fC1i91o23pM2-uN-sO19U89D6Z1T8fC-T2m55fE")
    download_dummy_image("physics.png", "https://fastly.picsum.photos/id/1025/400/300.jpg?hmac=n_LgH0dK1wB2pY1R8T9U0C-T2m55fE")

    tutor = Usuario.objects.filter(rol__nombre="tutor").first()
    materias = Subject.objects.all()
    
    if not tutor or not materias:
        return

    # Cuestionario 1: Programación/Matemáticas
    q1, created1 = Questionnaire.objects.get_or_create(
        title="Evaluación de Álgebra y Matrices",
        defaults={
            "description": "Demuestra tus conocimientos en multiplicación de matrices y sistemas lineales.",
            "teacher": tutor,
            "subject": materias.filter(code="ALG101").first(),
            "deadline": date.today() + timedelta(days=10),
            "allowed_attempts": 2,
            "is_active": True
        }
    )
    if created1:
        command.stdout.write(command.style.SUCCESS(f"   ✓ Cuestionario: {q1.title}"))
        
        # Pregunta 1 con Imagen
        p1 = Question.objects.create(
            questionnaire=q1,
            statement="Dada la siguiente matriz expuesta en la imagen, ¿cuál es su determinante?",
            image="questions/math.png",
            question_type="multiple_choice",
            order=1,
            max_score=5.0
        )
        QuestionOption.objects.create(question=p1, text="Determinante = 0", is_correct=False)
        QuestionOption.objects.create(question=p1, text="Determinante = 1", is_correct=True)
        QuestionOption.objects.create(question=p1, text="Determinante = -1", is_correct=False)
        
        # Pregunta 2 tipo boolean
        p2 = Question.objects.create(
            questionnaire=q1,
            statement="¿Toda matriz cuadrada tiene inversa?",
            question_type="boolean",
            order=2,
            max_score=5.0
        )
        QuestionOption.objects.create(question=p2, text="Verdadero", is_correct=False)
        QuestionOption.objects.create(question=p2, text="Falso", is_correct=True)

    # Cuestionario 2: Física
    q2, created2 = Questionnaire.objects.get_or_create(
        title="Prueba de Física I: Cinemática",
        defaults={
            "description": "Responde las preguntas relacionadas con la cinemática de partículas y caída libre.",
            "teacher": tutor,
            "subject": materias.filter(code="FIS101").first(),
            "deadline": date.today() + timedelta(days=7),
            "allowed_attempts": 1,
            "is_active": True
        }
    )
    if created2:
        command.stdout.write(command.style.SUCCESS(f"   ✓ Cuestionario: {q2.title}"))
        
        # Pregunta con Imagen de Física
        p3 = Question.objects.create(
            questionnaire=q2,
            statement="De acuerdo con la trayectoria y el diagrama de la imagen, ¿cuál es la aceleración en el punto máximo?",
            image="questions/physics.png",
            question_type="multiple_choice",
            order=1,
            max_score=10.0
        )
        QuestionOption.objects.create(question=p3, text="9.8 m/s² hacia abajo", is_correct=True)
        QuestionOption.objects.create(question=p3, text="0 m/s²", is_correct=False)
        QuestionOption.objects.create(question=p3, text="9.8 m/s² hacia arriba", is_correct=False)
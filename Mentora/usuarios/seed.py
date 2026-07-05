from datetime import date, datetime, timedelta, time

from usuarios.models import Rol, Usuario

from tutorias.models import (
    Subject,
    TutorAvailability,
    TutorSubject,
    TutoringSession,
    TutoringParticipation,
)


# ============================================================
# ROLES
# ============================================================

def create_roles(command):
    """
    Crea los roles básicos del sistema.
    """

    roles = [
        "admin",
        "profesor",
        "tutor",
        "estudiante",
    ]

    command.stdout.write("Creando roles...")

    for nombre in roles:

        _, created = Rol.objects.get_or_create(
            nombre=nombre
        )

        if created:

            command.stdout.write(
                command.style.SUCCESS(
                    f"   ✓ {nombre}"
                )
            )

        else:

            command.stdout.write(
                command.style.WARNING(
                    f"   • {nombre} ya existe"
                )
            )


# ============================================================
# USUARIOS
# ============================================================

def create_users(command):
    """
    Crea usuarios de prueba.
    """

    command.stdout.write("")
    command.stdout.write("Creando usuarios...")

    users = [

        {
            "nombre": "Administrador",
            "apellido": "Sistema",
            "correo": "admin@mentora.com",
            "password": "Admin123",
            "rol": "admin",
        },

        {
            "nombre": "Profesor",
            "apellido": "Demo",
            "correo": "profesor@mentora.com",
            "password": "Profesor123",
            "rol": "profesor",
        },

        {
            "nombre": "Tutor",
            "apellido": "Demo",
            "correo": "tutor@mentora.com",
            "password": "Tutor123",
            "rol": "tutor",
        },

        {
            "nombre": "Estudiante",
            "apellido": "Demo",
            "correo": "estudiante@mentora.com",
            "password": "Estudiante123",
            "rol": "estudiante",
        },

    ]

    for data in users:

        rol = Rol.objects.get(
            nombre=data["rol"]
        )

        usuario, created = Usuario.objects.get_or_create(
            correo=data["correo"],
            defaults={
                "nombre": data["nombre"],
                "apellido": data["apellido"],
                "rol": rol,
            }
        )

        if created:

            usuario.set_password(
                data["password"]
            )

            usuario.save()

            command.stdout.write(
                command.style.SUCCESS(
                    f"   ✓ {usuario.correo}"
                )
            )

        else:

            usuario.nombre = data["nombre"]
            usuario.apellido = data["apellido"]
            usuario.rol = rol

            usuario.set_password(
                data["password"]
    )

    usuario.save()

    command.stdout.write(

        command.style.WARNING(

            f"   • {usuario.correo} actualizado"

        )

    )

# ============================================================
# MATERIAS
# ============================================================

def create_subjects(command):
    """
    Crea las materias del sistema.
    """

    command.stdout.write("")
    command.stdout.write("Creando materias...")

    subjects = [

        (
            "Programación I",
            "PRG101",
            "Introducción a programación"
        ),

        (
            "Bases de Datos",
            "BD201",
            "Modelo relacional y SQL"
        ),

        (
            "Álgebra Lineal",
            "ALG101",
            "Matrices y vectores"
        ),

        (
            "Cálculo I",
            "CAL101",
            "Límites y derivadas"
        ),

        (
            "Física I",
            "FIS101",
            "Mecánica clásica"
        ),

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

            command.stdout.write(
                command.style.SUCCESS(
                    f"   ✓ {name}"
                )
            )

        else:

            command.stdout.write(
                command.style.WARNING(
                    f"   • {name} ya existe"
                )
            )


# ============================================================
# TUTOR - MATERIAS
# ============================================================

def create_tutor_subjects(command):

    command.stdout.write("")
    command.stdout.write("Asignando materias al tutor...")

    tutor = Usuario.objects.get(
        correo="tutor@mentora.com"
    )

    materias = Subject.objects.all()

    for materia in materias:

        _, created = TutorSubject.objects.get_or_create(
            tutor=tutor,
            subject=materia
        )

        if created:

            command.stdout.write(
                command.style.SUCCESS(
                    f"   ✓ {materia.name}"
                )
            )

        else:

            command.stdout.write(
                command.style.WARNING(
                    f"   • {materia.name} ya asignada"
                )
            )


# ============================================================
# DISPONIBILIDAD
# ============================================================

def create_availability(command):

    command.stdout.write("")
    command.stdout.write("Creando disponibilidad...")

    tutor = Usuario.objects.get(
        correo="tutor@mentora.com"
    )

    schedules = [

        (1, time(8, 0), time(10, 0)),
        (2, time(10, 0), time(12, 0)),
        (3, time(14, 0), time(16, 0)),
        (4, time(8, 0), time(10, 0)),
        (5, time(10, 0), time(12, 0)),

    ]

    for day, start, end in schedules:

        _, created = TutorAvailability.objects.get_or_create(

            tutor=tutor,
            day_of_week=day,
            start_time=start,
            end_time=end,

            defaults={
                "is_available": True
            }

        )

        if created:

            command.stdout.write(
                command.style.SUCCESS(
                    f"   ✓ Día {day}"
                )
            )

        else:

            command.stdout.write(
                command.style.WARNING(
                    f"   • Día {day} ya existe"
                )
            )

# ============================================================
# TUTORÍAS
# ============================================================

def create_sessions(command):

    command.stdout.write("")
    command.stdout.write("Creando tutorías...")

    materias = list(
        Subject.objects.all().order_by("id")
    )

    if len(materias) < 2:

        command.stdout.write(
            command.style.ERROR(
                "No existen suficientes materias."
            )
        )

        return

    sessions = [

        {
            "subject": materias[0],
            "date": date.today() + timedelta(days=2),
            "start": time(8, 0),
            "end": time(10, 0),
        },

        {
            "subject": materias[1],
            "date": date.today() + timedelta(days=3),
            "start": time(10, 0),
            "end": time(12, 0),
        },

        {
            "subject": materias[2],
            "date": date.today() + timedelta(days=5),
            "start": time(14, 0),
            "end": time(16, 0),
        },

    ]

    for data in sessions:

        session, created = TutoringSession.objects.get_or_create(

            subject=data["subject"],
            date=data["date"],
            start_time=data["start"],
            end_time=data["end"],

            defaults={

                "status": "agendada",

                "cancellation_deadline":
                    datetime.combine(
                        data["date"],
                        data["start"]
                    ) - timedelta(hours=24),

                "reschedule_count": 0,

            }

        )

        if created:

            command.stdout.write(

                command.style.SUCCESS(

                    f"   ✓ Tutoría {data['subject'].name}"

                )

            )

        else:

            command.stdout.write(

                command.style.WARNING(

                    f"   • Tutoría {data['subject'].name} ya existe"

                )

            )

# ============================================================
# PARTICIPANTES
# ============================================================

def create_participations(command):

    command.stdout.write("")
    command.stdout.write("Asignando participantes...")

    tutor = Usuario.objects.get(
        correo="tutor@mentora.com"
    )

    estudiante = Usuario.objects.get(
        correo="estudiante@mentora.com"
    )

    sesiones = TutoringSession.objects.all()

    for session in sesiones:

        _, created = TutoringParticipation.objects.get_or_create(

            session=session,
            user=tutor,

            defaults={

                "role_in_session": "tutor"

            }

        )

        if created:

            command.stdout.write(

                command.style.SUCCESS(

                    f"   ✓ Tutor -> {session.subject.name}"

                )

            )

        _, created = TutoringParticipation.objects.get_or_create(

            session=session,
            user=estudiante,

            defaults={

                "role_in_session": "estudiante"

            }

        )

        if created:

            command.stdout.write(

                command.style.SUCCESS(

                    f"   ✓ Estudiante -> {session.subject.name}"

                )

            )

    command.stdout.write("")

    command.stdout.write(

        command.style.SUCCESS(

            "Datos de prueba creados correctamente."

        )

    )
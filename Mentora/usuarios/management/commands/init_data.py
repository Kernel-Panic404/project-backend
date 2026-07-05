from django.core.management.base import BaseCommand

from usuarios.seed import (
    create_roles,
    create_users,
    create_subjects,
    create_tutor_subjects,
    create_availability,
    create_sessions,
    create_participations,
)


class Command(BaseCommand):

    help = "Inicializa todos los datos básicos del sistema."

    def handle(self, *args, **kwargs):

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                "INICIALIZANDO BASE DE DATOS"
            )
        )
        self.stdout.write("=" * 60)

        create_roles(self)

        create_users(self)

        create_subjects(self)

        create_tutor_subjects(self)

        create_availability(self)

        create_sessions(self)

        create_participations(self)

        self.stdout.write("")
        self.stdout.write("=" * 60)

        self.stdout.write(

            self.style.SUCCESS(

                "Inicialización finalizada correctamente."

            )

        )

        self.stdout.write("=" * 60)
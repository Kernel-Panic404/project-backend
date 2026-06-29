#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Iniciando contenedor de Django...${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"

# Esperar a que PostgreSQL esté disponible
echo -e "${YELLOW}⏳ Esperando a que PostgreSQL esté disponible...${NC}"

for i in {1..30}; do
  if nc -z $DB_HOST $DB_PORT 2>/dev/null; then
    echo -e "${GREEN}✓ PostgreSQL está disponible${NC}"
    break
  fi
  if [ $i -eq 30 ]; then
    echo -e "${RED}✗ PostgreSQL no está disponible después de 30 intentos${NC}"
    exit 1
  fi
  sleep 1
done

# Ejecutar migraciones
echo -e "${YELLOW}📦 Ejecutando migraciones de base de datos...${NC}"
python manage.py migrate --noinput

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Migraciones completadas exitosamente${NC}"
else
  echo -e "${RED}✗ Error al ejecutar migraciones${NC}"
  exit 1
fi

# Crear roles y superusuario
echo -e "${YELLOW}👤 Configurando roles y superusuario...${NC}"

python manage.py shell << END
from usuarios.models import Usuario, Rol
import os

try:
    # Crear roles si no existen
    roles_default = ['Admin', 'Profesor', 'Tutor', 'Estudiante']
    for rol_nombre in roles_default:
        rol, created = Rol.objects.get_or_create(nombre=rol_nombre)
        if created:
            print(f"  ✓ Rol '{rol_nombre}' creado")
        else:
            print(f"  ✓ Rol '{rol_nombre}' ya existe")

    # Crear superusuario si no existe
    admin_correo = 'admin@mentora.com'
    if not Usuario.objects.filter(correo=admin_correo).exists():
        admin = Usuario.objects.create(
            nombre='Admin',
            apellido='Sistema',
            correo=admin_correo,
            activo=True
        )
        admin.set_password('admin123')
        admin.rol = Rol.objects.get(nombre='Admin')
        admin.save()
        print(f"  ✓ Superusuario creado: {admin_correo} / admin123")
    else:
        print(f"  ✓ Superusuario ya existe: {admin_correo}")

    print("")
except Exception as e:
    print(f"  ✗ Error al crear roles/superusuario: {e}")

END

# Colectar archivos estáticos (opcional pero recomendado)
echo -e "${YELLOW}📁 Recolectando archivos estáticos...${NC}"
python manage.py collectstatic --noinput 2>/dev/null || true

echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Sistema listo. Iniciando servidor Django...${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🌐 Servidor disponible en: http://localhost:8000${NC}"
echo -e "${GREEN}📊 Admin Django en: http://localhost:8000/admin/${NC}"
echo -e "${GREEN}   Usuario: admin@mentora.com${NC}"
echo -e "${GREEN}   Contraseña: admin123${NC}"
echo ""

# Iniciar servidor Django
python manage.py runserver 0.0.0.0:8000

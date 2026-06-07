#!/bin/bash
# ============================================================
# setup.sh - Script de configuracion inicial del proyecto Mentora
# Compatible con: Linux y macOS
# Uso: bash setup.sh
# ============================================================


# ------------------------------------------------------------
# BLOQUE 1: Verificacion de dependencias del sistema
# ------------------------------------------------------------

echo ">>> Verificando Docker..."
docker --version || { echo "ERROR: Docker no esta instalado."; exit 1; }

echo ">>> Verificando Docker Compose..."
docker compose version || { echo "ERROR: Docker Compose no esta disponible."; exit 1; }


# ------------------------------------------------------------
# BLOQUE 2: Construccion de imagenes Docker
# ------------------------------------------------------------

echo ">>> Construyendo imagen de la aplicacion..."
docker compose build


# ------------------------------------------------------------
# BLOQUE 3: Levantamiento de servicios
# ------------------------------------------------------------

echo ">>> Levantando base de datos y aplicacion..."
docker compose up -d


# ------------------------------------------------------------
# BLOQUE 4: Espera a que la base de datos este lista
# ------------------------------------------------------------

echo ">>> Esperando que la base de datos este disponible..."
sleep 8


# ------------------------------------------------------------
# BLOQUE 5: Migraciones de Django
# ------------------------------------------------------------

echo ">>> Ejecutando migraciones de base de datos..."
docker compose exec web python manage.py migrate


# ------------------------------------------------------------
# BLOQUE 6: Pruebas basicas del proyecto
# ------------------------------------------------------------

echo ">>> Ejecutando pruebas basicas..."
docker compose exec web python manage.py test usuarios --verbosity=1


# ------------------------------------------------------------
# BLOQUE 7: Confirmacion final
# ------------------------------------------------------------

echo ""
echo "============================================================"
echo " Proyecto Mentora levantado correctamente"
echo " API disponible en: http://localhost:8000"
echo " Admin disponible en: http://localhost:8000/admin"
echo "============================================================"

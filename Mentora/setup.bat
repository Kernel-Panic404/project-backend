@echo off
REM ============================================================
REM setup.bat - Script de configuracion inicial del proyecto Mentora
REM Compatible con: Windows
REM Uso: Doble click o ejecutar en cmd como administrador
REM ============================================================


REM ------------------------------------------------------------
REM BLOQUE 1: Verificacion de dependencias del sistema
REM ------------------------------------------------------------

echo >>> Verificando Docker...
docker --version
IF ERRORLEVEL 1 ( echo ERROR: Docker no esta instalado. & exit /b 1 )

echo >>> Verificando Docker Compose...
docker compose version
IF ERRORLEVEL 1 ( echo ERROR: Docker Compose no esta disponible. & exit /b 1 )


REM ------------------------------------------------------------
REM BLOQUE 2: Construccion de imagenes Docker
REM ------------------------------------------------------------

echo >>> Construyendo imagen de la aplicacion...
docker compose build


REM ------------------------------------------------------------
REM BLOQUE 3: Levantamiento de servicios
REM ------------------------------------------------------------

echo >>> Levantando base de datos y aplicacion...
docker compose up -d


REM ------------------------------------------------------------
REM BLOQUE 4: Espera a que la base de datos este lista
REM ------------------------------------------------------------

echo >>> Esperando que la base de datos este disponible...
timeout /t 8 /nobreak


REM ------------------------------------------------------------
REM BLOQUE 5: Migraciones de Django
REM ------------------------------------------------------------

echo >>> Ejecutando migraciones de base de datos...
docker compose exec web python manage.py migrate


REM ------------------------------------------------------------
REM BLOQUE 6: Pruebas basicas del proyecto
REM ------------------------------------------------------------

echo >>> Ejecutando pruebas basicas...
docker compose exec web python manage.py test usuarios --verbosity=1


REM ------------------------------------------------------------
REM BLOQUE 7: Confirmacion final
REM ------------------------------------------------------------

echo.
echo ============================================================
echo  Proyecto Mentora levantado correctamente
echo  API disponible en: http://localhost:8000
echo  Admin disponible en: http://localhost:8000/admin
echo ============================================================

pause

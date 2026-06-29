FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-traditional \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/staticfiles

# Exponer puerto de Django
EXPOSE 8000

# Iniciar servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
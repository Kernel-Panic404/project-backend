FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-traditional \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/staticfiles

# Dar permisos de ejecución al entrypoint
RUN chmod +x entrypoint.sh

# Exponer puerto 8000 para Django
EXPOSE 8000

# Usar el entrypoint que ejecuta migraciones y luego inicia Django
ENTRYPOINT ["/app/entrypoint.sh"]

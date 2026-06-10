FROM python:3.12-slim

# Evitar buffering en stdout y crear .pyc
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar psycopg y utilidades de base de datos
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar la caché de capas de Docker
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copiar el código fuente
# Es fundamental copiar ambos porque el backend sirve los templates estáticos del web
COPY backend /app/backend
COPY web /app/web

# Establecer el directorio de trabajo donde está el punto de entrada de la app
WORKDIR /app/backend

# Exponer el puerto donde correrá Gunicorn
EXPOSE 5000

# Comando por defecto para iniciar el servidor WSGI en producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]

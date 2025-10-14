# Imagen base
FROM python:3.11-slim

# Evita archivos pyc y asegura logs en stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema necesarias para mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Copiar entrypoint
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/entrypoint.sh

# Variables de entorno por defecto
ENV DJANGO_SETTINGS_MODULE=config.settings.prod

# Exponer puerto del servidor
EXPOSE 8000

# Entrypoint que espera DB, migra, colecta static y arranca gunicorn
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
#!/usr/bin/env sh
set -e

echo "Esperando a que MySQL esté disponible en ${DB_HOST}:${DB_PORT}..."
if command -v mysqladmin >/dev/null 2>&1; then
  export MYSQL_PWD="${MYSQL_ROOT_PASSWORD}"
  until mysqladmin ping --protocol=TCP -h"${DB_HOST}" -P"${DB_PORT}" -uroot --silent; do
    echo "MySQL no disponible aún. Reintentando en 2s..."
    sleep 2
  done
else
  echo "mysqladmin no encontrado, usando verificación con Python..."
  python - <<'PY'
import os, time
import MySQLdb
host = os.getenv('DB_HOST', 'db')
port = int(os.getenv('DB_PORT', '3306'))
user = 'root'
pwd  = os.getenv('MYSQL_ROOT_PASSWORD', '')
while True:
    try:
        conn = MySQLdb.connect(host=host, port=port, user=user, passwd=pwd)
        conn.close()
        break
    except Exception:
        print("MySQL no disponible aún. Reintentando en 2s...")
        time.sleep(2)
PY
fi

echo "MySQL disponible. Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Colectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Arrancando servidor WSGI (gunicorn)..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --threads 2 --timeout 120 --graceful-timeout 120 --log-level info --access-logfile -
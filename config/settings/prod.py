"""
Configuración para el entorno de producción.
"""

from .base import *
import os
import socket
import logging

# Configuración de entorno
DEBUG = os.getenv("DEBUG", "False") == "True"

# ALLOWED_HOSTS - Configuración dinámica
ALLOWED_HOSTS = []
allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "")
if allowed_hosts_env == "*":
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]

# Si no hay hosts específicos, agregar los básicos
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.2.66.1", "172.18.0.3"]

SECRET_KEY = os.getenv("SECRET_KEY")
if not DEBUG and (
    not SECRET_KEY or SECRET_KEY.startswith("django-insecure") or len(SECRET_KEY) < 50
):
    raise Exception("Configura un SECRET_KEY fuerte en .env para producción")

# Seguridad (unificada y configurable por .env)
def env_bool(name, default):
    return os.getenv(name, str(default)).lower() in ("true", "1", "yes")

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", 0))
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Configuración de proxy y SSL para entorno LAN
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "http")
SECURE_SSL_REDIRECT = False
SECURE_REDIRECT_EXEMPT = [r"^.*$"]

# Configuración de cookies de seguridad
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)

# Base de datos (MySQL)
DB_ENGINE = os.getenv("DB_ENGINE", "mysql")
if DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "agrosmart"),
            "USER": os.getenv("DB_USER", "agrosmart_user"),
            "PASSWORD": os.getenv("DB_PASSWORD", "agrosmart_pass"),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            "CONN_MAX_AGE": 60,
        }
    }

# Email configuration para producción
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Static y Media (asegurar rutas para Docker)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ============================================================================
# CONFIGURACIÓN CSRF OPTIMIZADA PARA DOCKER + LAN
# ============================================================================

# Configurar CSRF_TRUSTED_ORIGINS desde .env únicamente
csrf_origins_env = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if csrf_origins_env:
    # Limpiar caracteres especiales y crear lista única
    origins = []
    for origin in csrf_origins_env.split(","):
        clean_origin = origin.strip().replace('`', '').replace('"', '').replace("'", '')
        if clean_origin and clean_origin not in origins:
            origins.append(clean_origin)
    CSRF_TRUSTED_ORIGINS = origins
else:
    # Valores por defecto si no hay configuración en .env
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://10.2.66.1:8000"
    ]

# Configuración de cookies CSRF
CSRF_COOKIE_HTTPONLY = os.getenv("CSRF_COOKIE_HTTPONLY", "False") == "True"
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
CSRF_USE_SESSIONS = os.getenv("CSRF_USE_SESSIONS", "False") == "True"
CSRF_COOKIE_AGE = int(os.getenv("CSRF_COOKIE_AGE", 31449600))  # 1 año por defecto
CSRF_COOKIE_DOMAIN = os.getenv("CSRF_COOKIE_DOMAIN", None)

# Configuración de cookies de sesión
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", 1209600))  # 2 semanas

# Función para obtener IPs locales del sistema
def get_local_ips():
    """Obtener IPs locales del sistema de manera segura"""
    ips = []
    try:
        # Obtener IP del hostname
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip and local_ip != "127.0.0.1":
            ips.append(local_ip)
    except Exception as e:
        logging.warning(f"No se pudo obtener IP local: {e}")
    
    return ips

# Agregar IPs locales detectadas (evitar duplicados)
local_ips = get_local_ips()
for ip in local_ips:
    if ip:
        origin = f"http://{ip}:8000"
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)

# Garantizar que la IP LAN fija esté incluida (refuerzo explícito)
if "http://10.2.66.1:8000" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append("http://10.2.66.1:8000")



# Vista personalizada para errores CSRF
CSRF_FAILURE_VIEW = os.getenv("CSRF_FAILURE_VIEW", "django.views.csrf.csrf_failure")

# Configuración condicional para DEBUG
if DEBUG:
    # Debug toolbar solo si está disponible
    try:
        import debug_toolbar
        if 'debug_toolbar' not in INSTALLED_APPS:
            INSTALLED_APPS += ['debug_toolbar']
        if 'debug_toolbar.middleware.DebugToolbarMiddleware' not in MIDDLEWARE:
            MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
        
        # IPs internas para debug toolbar
        INTERNAL_IPS = ['127.0.0.1', '172.18.0.1', '10.2.66.1'] + local_ips
    except ImportError:
        pass

# Configuración de logging detallado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.security.csrf': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Forzar la escritura inmediata de logs
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/django.log'),
        logging.StreamHandler()
    ]
)

# Logging informativo del arranque
logging.info(f"🚀 Django iniciado en modo {'DEBUG' if DEBUG else 'PRODUCCIÓN'}")
logging.info(f"🌐 Hosts permitidos: {ALLOWED_HOSTS}")
logging.info(f"🔒 Orígenes CSRF confiables: {CSRF_TRUSTED_ORIGINS}")

# Información de debug al iniciar
if DEBUG:
    import sys
    print(f"[DEBUG] CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}", file=sys.stderr, flush=True)
    print(f"[DEBUG] IPs locales detectadas: {local_ips}", file=sys.stderr, flush=True)
    print(f"[DEBUG] ALLOWED_HOSTS: {ALLOWED_HOSTS}", file=sys.stderr, flush=True)
    print(f"[DEBUG] CSRF_COOKIE_SAMESITE: {CSRF_COOKIE_SAMESITE}", file=sys.stderr, flush=True)
    print(f"[DEBUG] SESSION_COOKIE_SAMESITE: {SESSION_COOKIE_SAMESITE}", file=sys.stderr, flush=True)
    print(f"[DEBUG] DEBUG MODE: {DEBUG}", file=sys.stderr, flush=True)
    print(f"[DEBUG] DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr, flush=True)
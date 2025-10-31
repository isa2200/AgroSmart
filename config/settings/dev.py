"""
Configuración para el entorno de desarrollo.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.2.66.1']

# Database - MySQL Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'agrosmart_db',
        'USER': 'root',  # Verifica que este sea tu usuario correcto
        'PASSWORD': '0000',  # Cambia por tu contraseña real de MySQL
        'HOST': 'localhost',
        'PORT': '3307',
        'OPTIONS': {
            'sql_mode': 'traditional',
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar (opcional)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# CSRF Configuration for development - IP fija
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://10.2.66.1:8000',
]

# Configuración de cookies para desarrollo
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
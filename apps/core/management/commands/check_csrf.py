from django.core.management.base import BaseCommand
from django.conf import settings
import os
import socket

class Command(BaseCommand):
    help = "Comando para verificar configuracion CSRF"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== DIAGNOSTICO CSRF ==="))
        
        # Configuracion basica
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        
        # CSRF Configuration
        self.stdout.write(f"CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NO DEFINIDO')}")
        self.stdout.write(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'NO DEFINIDO')}")
        self.stdout.write(f"CSRF_COOKIE_SAMESITE: {getattr(settings, 'CSRF_COOKIE_SAMESITE', 'NO DEFINIDO')}")
        self.stdout.write(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'NO DEFINIDO')}")
        self.stdout.write(f"SESSION_COOKIE_SAMESITE: {getattr(settings, 'SESSION_COOKIE_SAMESITE', 'NO DEFINIDO')}")
        self.stdout.write(f"CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'NO DEFINIDO')}")
        self.stdout.write(f"CSRF_USE_SESSIONS: {getattr(settings, 'CSRF_USE_SESSIONS', 'NO DEFINIDO')}")
        
        # Network info
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.stdout.write(f"HOSTNAME: {hostname}")
            self.stdout.write(f"LOCAL_IP: {local_ip}")
        except:
            self.stdout.write("No se pudo obtener informacion de red")
        
        # Environment variables
        self.stdout.write("\n=== VARIABLES DE ENTORNO RELEVANTES ===")
        env_vars = ["DB_HOST", "DB_PORT", "ALLOWED_HOSTS", "CSRF_TRUSTED_ORIGINS"]
        for var in env_vars:
            self.stdout.write(f"{var}: {os.environ.get(var, 'NO DEFINIDO')}")
        
        self.stdout.write(self.style.SUCCESS("\n=== FIN DIAGNOSTICO ==="))
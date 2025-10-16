from django.core.management.base import BaseCommand
from django.conf import settings
from django.middleware.csrf import get_token
from django.test import RequestFactory
import os

class Command(BaseCommand):
    help = "Comando para debuggear CSRF en detalle"

    def handle(self, *args, **options):
        self.stdout.write("=== DEBUG CSRF DETALLADO ===")
        
        # Configuración actual
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'No definido')}")
        self.stdout.write(f"CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'No definido')}")
        self.stdout.write(f"CSRF_COOKIE_SAMESITE: {getattr(settings, 'CSRF_COOKIE_SAMESITE', 'No definido')}")
        self.stdout.write(f"CSRF_USE_SESSIONS: {getattr(settings, 'CSRF_USE_SESSIONS', 'No definido')}")
        self.stdout.write(f"CSRF_COOKIE_DOMAIN: {getattr(settings, 'CSRF_COOKIE_DOMAIN', 'No definido')}")
        self.stdout.write(f"CSRF_COOKIE_PATH: {getattr(settings, 'CSRF_COOKIE_PATH', 'No definido')}")
        
        self.stdout.write(f"\nCSRF_TRUSTED_ORIGINS:")
        for origin in getattr(settings, 'CSRF_TRUSTED_ORIGINS', []):
            self.stdout.write(f"  - {origin}")
        
        # Probar generación de token CSRF
        self.stdout.write("\n=== PRUEBA DE GENERACION DE TOKEN ===")
        factory = RequestFactory()
        
        test_hosts = ['localhost:8000', '127.0.0.1:8000', '172.30.0.58:8000']
        
        for host in test_hosts:
            try:
                request = factory.get('/', HTTP_HOST=host)
                token = get_token(request)
                self.stdout.write(f"Host '{host}': Token generado = {token[:20]}...")
            except Exception as e:
                self.stdout.write(f"Host '{host}': ERROR = {e}")
        
        # Verificar middleware
        self.stdout.write("\n=== MIDDLEWARE CSRF ===")
        csrf_middleware = [m for m in settings.MIDDLEWARE if 'csrf' in m.lower()]
        self.stdout.write(f"Middleware CSRF encontrado: {csrf_middleware}")
        
        # Variables de entorno críticas
        self.stdout.write("\n=== VARIABLES DE ENTORNO CSRF ===")
        csrf_vars = [
            'CSRF_TRUSTED_ORIGINS',
            'CSRF_COOKIE_SECURE', 
            'CSRF_COOKIE_HTTPONLY',
            'CSRF_COOKIE_SAMESITE',
            'CSRF_USE_SESSIONS',
            'CSRF_COOKIE_DOMAIN'
        ]
        
        for var in csrf_vars:
            value = os.getenv(var, 'No definida')
            self.stdout.write(f"{var}: {value}")
        
        self.stdout.write("\n=== INSTRUCCIONES DE PRUEBA ===")
        self.stdout.write("1. Reinicia Docker: docker-compose restart")
        self.stdout.write("2. Accede a http://172.30.0.58:8000 desde otro dispositivo")
        self.stdout.write("3. Abre las herramientas de desarrollador (F12)")
        self.stdout.write("4. Ve a la pestaña 'Network' o 'Red'")
        self.stdout.write("5. Intenta hacer login y captura el error exacto")
        self.stdout.write("6. Revisa las cookies en 'Application' > 'Cookies'")
        
        self.stdout.write("\n=== FIN DEBUG ===")
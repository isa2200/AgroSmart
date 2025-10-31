from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.middleware.csrf import get_token
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Diagnostica problemas de cookies CSRF'

    def handle(self, *args, **options):
        print("=== DIAGNÓSTICO DE COOKIES CSRF ===")
        
        # Configuraciones actuales
        print(f"CSRF_COOKIE_DOMAIN: {getattr(settings, 'CSRF_COOKIE_DOMAIN', 'No definido')}")
        print(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', False)}")
        print(f"CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', False)}")
        print(f"CSRF_COOKIE_SAMESITE: {getattr(settings, 'CSRF_COOKIE_SAMESITE', 'Lax')}")
        print(f"CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])}")
        
        # Simular requests desde diferentes hosts
        factory = RequestFactory()
        hosts = ['localhost:8000', '127.0.0.1:8000', '10.2.66.1:8000']
        
        print("\n=== SIMULACIÓN DE REQUESTS ===")
        for host in hosts:
            try:
                request = factory.get('/', HTTP_HOST=host)
                token = get_token(request)
                print(f"Host {host}: Token generado ✓ ({token[:16]}...)")
            except Exception as e:
                print(f"Host {host}: ERROR - {e}")
        
        print("\n=== RECOMENDACIONES ===")
        print("1. Reinicia Docker: docker-compose restart")
        print("2. Accede primero a http://localhost:8000 y verifica que funcione")
        print("3. Luego accede a http://10.2.66.1:8000")
        print("4. Si persiste el error, verifica las cookies en DevTools:")
        print("   - F12 > Application > Cookies")
        print("   - Busca 'csrftoken' y verifica su dominio")
        print("5. Intenta limpiar cookies del navegador para 10.2.66.1")
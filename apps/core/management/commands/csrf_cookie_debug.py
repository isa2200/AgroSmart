from django.core.management.base import BaseCommand
from django.conf import settings
from django.middleware.csrf import get_token
from django.test import RequestFactory
from django.http import HttpRequest
import os

class Command(BaseCommand):
    help = 'Diagnostica problemas específicos de cookies CSRF'

    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNÓSTICO DE COOKIES CSRF ===")
        
        # Configuraciones actuales
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
        self.stdout.write(f"CSRF_COOKIE_HTTPONLY: {settings.CSRF_COOKIE_HTTPONLY}")
        self.stdout.write(f"CSRF_COOKIE_SAMESITE: {settings.CSRF_COOKIE_SAMESITE}")
        self.stdout.write(f"CSRF_COOKIE_DOMAIN: {settings.CSRF_COOKIE_DOMAIN}")
        self.stdout.write(f"CSRF_COOKIE_PATH: {settings.CSRF_COOKIE_PATH}")
        self.stdout.write(f"CSRF_USE_SESSIONS: {settings.CSRF_USE_SESSIONS}")
        
        self.stdout.write("\n=== CSRF_TRUSTED_ORIGINS ===")
        for origin in settings.CSRF_TRUSTED_ORIGINS:
            self.stdout.write(f"  - {origin}")
        
        # Simular requests desde diferentes hosts
        self.stdout.write("\n=== SIMULACIÓN DE REQUESTS ===")
        factory = RequestFactory()
        
        test_hosts = [
            ('localhost:8000', 'http://localhost:8000'),
            ('127.0.0.1:8000', 'http://127.0.0.1:8000'),
            ('172.30.0.58:8000', 'http://172.30.0.58:8000'),
        ]
        
        for host, origin in test_hosts:
            try:
                request = factory.get('/', HTTP_HOST=host, HTTP_ORIGIN=origin)
                request.META['HTTP_REFERER'] = f'{origin}/'
                
                # Intentar generar token CSRF
                token = get_token(request)
                self.stdout.write(f"✓ Host {host}: Token generado correctamente")
                
                # Verificar si el origen está en CSRF_TRUSTED_ORIGINS
                if origin in settings.CSRF_TRUSTED_ORIGINS:
                    self.stdout.write(f"  ✓ Origen {origin} está en CSRF_TRUSTED_ORIGINS")
                else:
                    self.stdout.write(f"  ✗ Origen {origin} NO está en CSRF_TRUSTED_ORIGINS")
                    
            except Exception as e:
                self.stdout.write(f"✗ Host {host}: Error - {str(e)}")
        
        self.stdout.write("\n=== RECOMENDACIONES ===")
        
        # Verificar configuración para acceso externo
        if settings.CSRF_COOKIE_SECURE and not settings.DEBUG:
            self.stdout.write("⚠️  CSRF_COOKIE_SECURE=True requiere HTTPS")
        
        if settings.CSRF_COOKIE_SAMESITE == 'Strict':
            self.stdout.write("⚠️  CSRF_COOKIE_SAMESITE='Strict' puede bloquear requests cross-origin")
        
        if settings.CSRF_COOKIE_DOMAIN:
            self.stdout.write(f"⚠️  CSRF_COOKIE_DOMAIN está configurado: {settings.CSRF_COOKIE_DOMAIN}")
        
        # Verificar si 172.30.0.58:8000 está en trusted origins
        target_origin = 'http://172.30.0.58:8000'
        if target_origin not in settings.CSRF_TRUSTED_ORIGINS:
            self.stdout.write(f"❌ {target_origin} NO está en CSRF_TRUSTED_ORIGINS")
        else:
            self.stdout.write(f"✅ {target_origin} está en CSRF_TRUSTED_ORIGINS")
        
        self.stdout.write("\n=== SOLUCIÓN RECOMENDADA ===")
        self.stdout.write("1. Asegúrate de que CSRF_COOKIE_SAMESITE='Lax' (no 'Strict')")
        self.stdout.write("2. Verifica que CSRF_COOKIE_SECURE=False para HTTP")
        self.stdout.write("3. Confirma que http://172.30.0.58:8000 está en CSRF_TRUSTED_ORIGINS")
        self.stdout.write("4. Reinicia Docker después de cambios: docker-compose restart")
        self.stdout.write("5. Limpia cookies del navegador antes de probar")
        
        self.stdout.write("\n=== COMANDO DE PRUEBA ===")
        self.stdout.write("Desde otro dispositivo, abre http://172.30.0.58:8000 y:")
        self.stdout.write("1. Abre DevTools (F12)")
        self.stdout.write("2. Ve a Application > Cookies")
        self.stdout.write("3. Verifica si existe la cookie 'csrftoken'")
        self.stdout.write("4. Si no existe, el problema está en la configuración de cookies")
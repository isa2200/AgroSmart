from django.core.management.base import BaseCommand
from django.conf import settings
from django.test import RequestFactory
from django.http import HttpResponse
import socket
import os

class Command(BaseCommand):
    help = "Comando para probar acceso desde diferentes IPs"

    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNOSTICO DE ACCESO POR IP ===")
        
        # Información básica
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'No definido')}")
        
        # Probar diferentes hosts
        test_hosts = [
            'localhost',
            '127.0.0.1', 
            '172.30.0.58',
            '172.18.0.3'
        ]
        
        self.stdout.write("\n=== PRUEBA DE VALIDACION DE HOSTS ===")
        
        factory = RequestFactory()
        
        for host in test_hosts:
            try:
                # Simular request con el host específico
                request = factory.get('/', HTTP_HOST=f'{host}:8000')
                
                # Verificar si el host está permitido
                if settings.ALLOWED_HOSTS == ['*'] or host in settings.ALLOWED_HOSTS:
                    host_status = "✅ PERMITIDO"
                else:
                    host_status = "❌ RECHAZADO"
                
                # Verificar CSRF
                csrf_origin = f'http://{host}:8000'
                if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
                    if csrf_origin in settings.CSRF_TRUSTED_ORIGINS:
                        csrf_status = "✅ CSRF OK"
                    else:
                        csrf_status = "❌ CSRF RECHAZADO"
                else:
                    csrf_status = "⚠️ CSRF NO CONFIGURADO"
                
                self.stdout.write(f"Host '{host}': {host_status} | {csrf_status}")
                
            except Exception as e:
                self.stdout.write(f"Host '{host}': ❌ ERROR - {e}")
        
        # Información de red actual
        self.stdout.write("\n=== INFORMACION DE RED ACTUAL ===")
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.stdout.write(f"Hostname del contenedor: {hostname}")
            self.stdout.write(f"IP principal del contenedor: {local_ip}")
            
            # Obtener todas las interfaces de red
            import subprocess
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            if result.returncode == 0:
                all_ips = result.stdout.strip().split()
                self.stdout.write(f"Todas las IPs del contenedor: {all_ips}")
            
        except Exception as e:
            self.stdout.write(f"Error obteniendo info de red: {e}")
        
        # Verificar middleware de seguridad
        self.stdout.write("\n=== MIDDLEWARE DE SEGURIDAD ===")
        middleware_list = settings.MIDDLEWARE
        security_middleware = [m for m in middleware_list if 'security' in m.lower()]
        self.stdout.write(f"Middleware de seguridad activo: {security_middleware}")
        
        # Configuraciones de seguridad relevantes
        security_settings = [
            'SECURE_SSL_REDIRECT',
            'SECURE_BROWSER_XSS_FILTER', 
            'SECURE_CONTENT_TYPE_NOSNIFF',
            'SECURE_HSTS_SECONDS',
            'SECURE_PROXY_SSL_HEADER'
        ]
        
        self.stdout.write("\n=== CONFIGURACIONES DE SEGURIDAD ===")
        for setting_name in security_settings:
            value = getattr(settings, setting_name, 'No definido')
            self.stdout.write(f"{setting_name}: {value}")
        
        self.stdout.write("\n=== RECOMENDACIONES ===")
        self.stdout.write("1. Verifica que no haya firewall bloqueando el puerto 8000")
        self.stdout.write("2. Asegúrate de que Docker esté exponiendo el puerto correctamente")
        self.stdout.write("3. Prueba acceder desde el mismo dispositivo usando la IP local")
        self.stdout.write("4. Revisa los logs de Django cuando accedas por la IP problemática")
        
        self.stdout.write("\n=== FIN DIAGNOSTICO ===")
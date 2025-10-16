from django.core.management.base import BaseCommand
from django.conf import settings
import socket
import os

class Command(BaseCommand):
    help = "Comando para verificar configuracion ALLOWED_HOSTS"

    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNOSTICO ALLOWED_HOSTS ===")
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        
        # Configuracion ALLOWED_HOSTS
        self.stdout.write("\n=== CONFIGURACION ALLOWED_HOSTS ===")
        self.stdout.write(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"ALLOWED_HOSTS (env): {os.getenv('ALLOWED_HOSTS')}")
        
        # Informacion de red
        self.stdout.write("\n=== INFORMACION DE RED ===")
        try:
            hostname = socket.gethostname()
            self.stdout.write(f"HOSTNAME: {hostname}")
            
            # Obtener todas las IPs del contenedor
            local_ip = socket.gethostbyname(hostname)
            self.stdout.write(f"LOCAL_IP: {local_ip}")
            
            # Obtener informacion adicional de red
            addrs = socket.getaddrinfo(hostname, None)
            ips = set()
            for addr in addrs:
                if addr[4][0] not in ['127.0.0.1', '::1']:
                    ips.add(addr[4][0])
            
            self.stdout.write(f"TODAS_LAS_IPS: {list(ips)}")
            
        except Exception as e:
            self.stdout.write(f"Error obteniendo info de red: {e}")
        
        # Variables de entorno relevantes
        self.stdout.write("\n=== VARIABLES DE ENTORNO RELEVANTES ===")
        env_vars = ['ALLOWED_HOSTS', 'DEBUG', 'DJANGO_SETTINGS_MODULE']
        for var in env_vars:
            value = os.getenv(var, 'No definida')
            self.stdout.write(f"{var}: {value}")
        
        # Prueba de validacion de hosts
        self.stdout.write("\n=== PRUEBA DE VALIDACION ===")
        test_hosts = ['localhost', '127.0.0.1', '172.18.0.3', '*']
        
        for host in test_hosts:
            if settings.ALLOWED_HOSTS == ['*'] or host in settings.ALLOWED_HOSTS:
                status = "PERMITIDO"
            else:
                status = "RECHAZADO"
            self.stdout.write(f"Host '{host}': {status}")
        
        self.stdout.write("\n=== FIN DIAGNOSTICO ===")
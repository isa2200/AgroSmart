import os
import django
import sys

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

username = 'IsabelCGJ'
password = '123456789L.'

try:
    user = User.objects.get(username=username)
    print(f"Usuario '{username}' encontrado.")
    user.set_password(password)
    user.save()
    print(f"Contraseña actualizada a: {password}")
    
    # Verificar perfil
    if not hasattr(user, 'perfilusuario'):
        print("Creando perfil de usuario...")
        PerfilUsuario.objects.create(usuario=user, rol='superusuario')
    
except User.DoesNotExist:
    print(f"Usuario '{username}' no existe. Creándolo...")
    user = User.objects.create_user(username=username, password=password, email='isabel@example.com')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    # Crear perfil
    if not hasattr(user, 'perfilusuario'):
        PerfilUsuario.objects.create(usuario=user, rol='superusuario')
    
    print(f"Usuario '{username}' creado exitosamente con contraseña: {password}")

print("Proceso completado.")

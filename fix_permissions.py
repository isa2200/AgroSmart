import os
import django
import sys

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

username = 'IsabelCGJ'

try:
    user = User.objects.get(username=username)
    print(f"Usuario '{username}' encontrado.")
    
    # Verificar y crear perfil si no existe
    if hasattr(user, 'perfilusuario'):
        perfil = user.perfilusuario
        print(f"Perfil actual: {perfil.rol}")
        if perfil.rol != 'superusuario':
            perfil.rol = 'superusuario'
            perfil.acceso_modulo_avicola = True
            perfil.puede_eliminar_registros = True
            perfil.save()
            print("Rol actualizado a 'superusuario' en PerfilUsuario.")
    else:
        print("El usuario no tiene perfil. Creando perfil de superusuario...")
        PerfilUsuario.objects.create(
            user=user, 
            rol='superusuario',
            acceso_modulo_avicola=True,
            puede_eliminar_registros=True
        )
        print("Perfil creado exitosamente.")

    # Asegurar que el usuario de Django también sea superuser
    if not user.is_superuser or not user.is_staff:
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("Permisos de Django (is_superuser, is_staff) actualizados.")

except User.DoesNotExist:
    print(f"Error: El usuario '{username}' no existe.")

print("Verificación de permisos completada.")

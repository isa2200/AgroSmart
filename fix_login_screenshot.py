import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'IsabelCGJ'
password = '123456789L.'

try:
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    if created:
        print(f"Usuario {username} creado exitosamente con permisos de superusuario.")
    else:
        print(f"Contraseña actualizada para el usuario existente {username}.")
        
    # Verificar perfil si existe
    try:
        if not hasattr(user, 'perfilusuario'):
            from apps.usuarios.models import PerfilUsuario
            PerfilUsuario.objects.create(usuario=user, rol='superusuario')
            print("Perfil de usuario creado.")
        else:
            user.perfilusuario.rol = 'superusuario'
            user.perfilusuario.save()
            print("Perfil de usuario actualizado a superusuario.")
    except Exception as e:
        print(f"Nota sobre perfil: {e}")

except Exception as e:
    print(f"Error al configurar usuario: {e}")

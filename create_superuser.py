
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from apps.usuarios.models import PerfilUsuario

User = get_user_model()
username = 'IsabelCGJ'
password = '123456789L.'  # Note the dot at the end

try:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"User {username} updated successfully with password '{password}'.")
    else:
        user = User.objects.create_superuser(username=username, email='', password=password)
        print(f"User {username} created successfully with password '{password}'.")

    # Asegurar que tenga perfil
    if not hasattr(user, 'perfilusuario'):
        PerfilUsuario.objects.create(usuario=user, rol='superusuario')
        print(f"PerfilUsuario created for {username}.")
    else:
        user.perfilusuario.rol = 'superusuario'
        user.perfilusuario.save()
        print(f"PerfilUsuario updated for {username}.")

except Exception as e:
    print(f"Error: {e}")

import os
import django
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

def ensure_user(username, password, role, email=""):
    try:
        user = User.objects.get(username=username)
        print(f"User '{username}' already exists.")
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, email=email, password=password)
        print(f"User '{username}' created.")

    if not hasattr(user, 'perfilusuario'):
        PerfilUsuario.objects.create(usuario=user, rol=role)
        print(f"Profile for '{username}' created with role '{role}'.")
    else:
        if user.perfilusuario.rol != role:
            user.perfilusuario.rol = role
            user.perfilusuario.save()
            print(f"Profile for '{username}' updated to role '{role}'.")
        else:
            print(f"Profile for '{username}' already has role '{role}'.")

    user.is_active = True
    user.save()
    print(f"User '{username}' is active.\n")

if __name__ == "__main__":
    ensure_user('vendedor', 'vendedor123', 'punto_blanco', 'vendedor@agrosmart.com')
    ensure_user('veterinario', 'vet123', 'veterinario', 'vet@agrosmart.com')

import os
import django
import secrets
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

def create_admin():
    username = "admin_principal"
    # Generate a random password
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    # Check if user exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists. Updating password...")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
    else:
        print(f"Creating new user '{username}'...")
        user = User.objects.create_superuser(username=username, email='admin@agrosmart.com', password=password)
    
    # Ensure PerfilUsuario exists
    perfil, created = PerfilUsuario.objects.get_or_create(user=user)
    perfil.rol = 'superusuario'
    perfil.save()
    
    print(f"\nSUCCESS! User created/updated.")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Role: {perfil.get_rol_display()}")

if __name__ == '__main__':
    create_admin()

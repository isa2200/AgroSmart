import os
import django
import sys

# Add the project root to the python path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

def create_veterinario():
    username = 'veterinario'
    email = 'veterinario@agrosmart.com'
    password = 'veterinario123'
    
    # Create or update User
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.email = email
        user.first_name = 'Veterinario'
        user.last_name = 'General'
        user.set_password(password)
        user.save()
        print(f"User {username} updated.")
    else:
        user = User.objects.create_user(username=username, email=email, password=password, first_name='Veterinario', last_name='General')
        print(f"User {username} created.")

    # Create or update Profile
    # Note: A signal might have created the profile already
    perfil, created = PerfilUsuario.objects.get_or_create(user=user)
    perfil.rol = 'veterinario'
    perfil.save()
    
    print(f"Profile for {username} set to role: {perfil.rol}")

if __name__ == '__main__':
    create_veterinario()

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

def create_veterinario():
    username = 'veterinario'
    email = 'veterinario@agrosmart.com'
    password = 'veterinario123'
    
    user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'first_name': 'Veterinario', 'last_name': 'General'})
    user.set_password(password)
    user.save()
    
    perfil, p_created = PerfilUsuario.objects.get_or_create(user=user)
    perfil.rol = 'veterinario'
    perfil.save()
    
    print(f"User {username} created/updated. Role set to {perfil.rol}")

if __name__ == '__main__':
    create_veterinario()

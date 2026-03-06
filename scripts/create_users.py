import os
import django
import sys

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

def create_users():
    # 1. Create Veterinario User
    username_vet = 'veterinario'
    email_vet = 'veterinario@agrosmart.com'
    password_vet = 'veterinario123'
    
    if User.objects.filter(username=username_vet).exists():
        user_vet = User.objects.get(username=username_vet)
        user_vet.email = email_vet
        user_vet.set_password(password_vet)
        user_vet.save()
        print(f"User {username_vet} updated.")
    else:
        user_vet = User.objects.create_user(username=username_vet, email=email_vet, password=password_vet, first_name='Veterinario', last_name='General')
        print(f"User {username_vet} created.")

    # Update Profile for Veterinario
    perfil_vet, created_vet = PerfilUsuario.objects.get_or_create(user=user_vet)
    perfil_vet.rol = 'veterinario'
    perfil_vet.save()
    print(f"Profile for {username_vet} set to role: {perfil_vet.rol}")

    # 2. Create Punto Blanco (Vendedor) User
    username_pb = 'vendedor'
    email_pb = 'vendedor@agrosmart.com'
    password_pb = 'vendedor123'
    
    if User.objects.filter(username=username_pb).exists():
        user_pb = User.objects.get(username=username_pb)
        user_pb.email = email_pb
        user_pb.set_password(password_pb)
        user_pb.save()
        print(f"User {username_pb} updated.")
    else:
        user_pb = User.objects.create_user(username=username_pb, email=email_pb, password=password_pb, first_name='Vendedor', last_name='Punto Blanco')
        print(f"User {username_pb} created.")

    # Update Profile for Punto Blanco
    perfil_pb, created_pb = PerfilUsuario.objects.get_or_create(user=user_pb)
    perfil_pb.rol = 'punto_blanco'
    perfil_pb.save()
    print(f"Profile for {username_pb} set to role: {perfil_pb.rol}")

if __name__ == '__main__':
    create_users()


import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

try:
    user = User.objects.get(username='vendedor')
    print(f"User: {user.username}")
    
    try:
        perfil = user.perfilusuario
        print(f"Role: {perfil.rol}")
        print(f"Active: {user.is_active}")
    except PerfilUsuario.DoesNotExist:
        print("PerfilUsuario does not exist!")
        
except User.DoesNotExist:
    print("User 'vendedor' does not exist!")

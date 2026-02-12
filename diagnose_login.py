import os
import sys
import django
from django.conf import settings

# Setup environment exactly as manage.py would for default dev
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# Initialize Django
sys.path.append(os.getcwd())
django.setup()

def diagnose():
    print(f"Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"Databases Config: {settings.DATABASES['default']['ENGINE']}")
    print(f"Database Name: {settings.DATABASES['default']['NAME']}")
    
    from django.contrib.auth.models import User
    from django.contrib.auth import authenticate
    
    username = 'IsabelCGJ'
    password = 'admin123'
    
    user = User.objects.filter(username=username).first()
    
    if user:
        print(f"\nUser '{username}' FOUND.")
        print(f"  ID: {user.id}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Is Superuser: {user.is_superuser}")
        
        # Check Profile
        try:
            profile = user.perfilusuario
            print(f"  Profile Found: Rol={profile.rol}")
        except Exception as e:
            print(f"  Profile ERROR: {e}")
            from apps.usuarios.models import PerfilUsuario
            print("  Creating profile...")
            PerfilUsuario.objects.create(usuario=user, rol='superusuario')
            print("  Profile created.")

        print(f"  Password Hash: {user.password[:20]}...")
        
        # Test authentication
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            print(f"  Authentication: SUCCESS")
        else:
            print(f"  Authentication: FAILED")
            print("  Attempting to fix password...")
            user.set_password(password)
            user.save()
            print("  Password reset. Retrying auth...")
            if authenticate(username=username, password=password):
                print("  Authentication: SUCCESS after reset")
            else:
                print("  Authentication: STILL FAILED")
    else:
        print(f"\nUser '{username}' NOT FOUND.")
        print("Existing users:")
        for u in User.objects.all():
            print(f"  - {u.username}")

if __name__ == "__main__":
    diagnose()

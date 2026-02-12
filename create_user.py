import os
import django
import sys
from pathlib import Path

# Load .env manually
env_path = Path(os.getcwd()) / '.env'
if env_path.exists():
    print("Loading .env file...")
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Set to dev settings but force MySQL
print("Configuring environment for MySQL with Dev settings...")
os.environ['USE_SQLITE'] = '0'  # Force MySQL in dev.py
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.dev' # Force dev settings, overwriting .env
os.environ['DB_HOST'] = '127.0.0.1' # Force localhost for DB connection from host

sys.path.append(os.getcwd())
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario

def create_or_update_user():
    username = 'IsabelCGJ'
    email = 'isaij385532@gmail.com'
    password = 'admin123'
    
    try:
        print(f"Attempting to connect to database and find user {username}...")
        user = User.objects.filter(username=username).first()
        
        if user:
            print(f"User '{username}' found. Resetting password...")
            user.set_password(password)
            user.save()
            print(f"SUCCESS: Password for '{username}' has been reset to '{password}'")
        else:
            print(f"WARNING: User '{username}' not found in this database.")
            # Optional: List users to see who is there
            print("Users found in DB:", [u.username for u in User.objects.all()])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_or_update_user()

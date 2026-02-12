import os
import django
from django.contrib.auth import get_user_model
from django.conf import settings

# Force SQLite settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
os.environ['USE_SQLITE'] = 'True' 

django.setup()

def update_sqlite():
    print(f"Current DB Engine: {settings.DATABASES['default']['ENGINE']}")
    if 'sqlite' not in settings.DATABASES['default']['ENGINE']:
        print("ERROR: Not connected to SQLite. Aborting.")
        return

    User = get_user_model()
    username = 'IsabelCGJ'
    password = '123456789L.'
    
    print(f"--- Checking SQLite ---")
    try:
        user = User.objects.get(username=username)
        print(f"User {username} found in SQLite.")
    except User.DoesNotExist:
        print(f"User {username} not found in SQLite. Creating...")
        user = User.objects.create_user(username=username, email='isabel@example.com')
    
    user.set_password(password)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"User {username} updated in SQLite: Active=True, Password set.")

if __name__ == "__main__":
    update_sqlite()

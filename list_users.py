import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    # Try default settings if dev fails
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'
    django.setup()

from django.contrib.auth.models import User

def list_users():
    print("Listing all users in the database:")
    users = User.objects.all()
    for u in users:
        print(f"- Username: {u.username}, Email: {u.email}, Is Active: {u.is_active}, Is Superuser: {u.is_superuser}")
        
    if not users.exists():
        print("No users found.")

if __name__ == "__main__":
    list_users()

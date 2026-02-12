import os
import sys
import django

# Setup environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
sys.path.append(os.getcwd())
django.setup()

from django.contrib.auth.models import User

def change_password():
    username = 'IsabelCGJ'
    new_password = '123456789L.'
    
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"SUCCESS: Password for '{username}' has been updated to '{new_password}'")
    except User.DoesNotExist:
        print(f"ERROR: User '{username}' not found.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    change_password()

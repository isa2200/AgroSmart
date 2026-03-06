import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User

def force_setup():
    username = 'IsabelCGJ'
    try:
        u = User.objects.get(username=username)
        u.set_password('123456789L.')
        u.is_active = True
        u.is_staff = True
        u.is_superuser = True
        u.save()
        print(f"User '{username}' updated: Password set, Active=True, Staff=True, Superuser=True")
    except User.DoesNotExist:
        print(f"User '{username}' not found, creating...")
        u = User.objects.create_superuser(username, 'isabel@example.com', '123456789L.')
        print(f"User '{username}' created successfully")

if __name__ == "__main__":
    force_setup()

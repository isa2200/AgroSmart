import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User

def reset_password():
    try:
        u = User.objects.get(username='dev')
        u.set_password('admin123')
        u.save()
        print("Password for user 'dev' has been reset to 'admin123'")
    except User.DoesNotExist:
        print("User 'dev' not found")

if __name__ == "__main__":
    reset_password()

import os
import django
from django.contrib.auth import get_user_model

print("--- Updating SQLite ---")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
os.environ['USE_SQLITE'] = 'True'
django.setup()

User = get_user_model()
try:
    user = User.objects.get(username='IsabelCGJ')
    user.set_password('123456789L.')
    user.save()
    print("SQLite: Password restored to '123456789L.'")
except User.DoesNotExist:
    print("SQLite: User not found")

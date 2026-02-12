import os
import django
from django.contrib.auth import get_user_model

print("--- SQLite ---")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
os.environ['USE_SQLITE'] = 'True'
django.setup()

User = get_user_model()
try:
    user = User.objects.get(username='IsabelCGJ')
    user.set_password('AgroSmart2025')
    user.save()
    print(f"Password for IsabelCGJ set to: AgroSmart2025 (SQLite)")
except User.DoesNotExist:
    print("User not found in SQLite")

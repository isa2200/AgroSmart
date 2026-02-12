import os
import django
from django.contrib.auth import get_user_model
from django.conf import settings

# Force SQLite settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
# We need to run this for BOTH SQLite and MySQL separately or just rely on the default behavior if we can swap env vars.
# Let's just do it for the current default (MySQL) and then SQLite if needed.
# Actually, let's just use the `sync_sqlite.py` approach again but simplified.

def set_password(username, password):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"Password for {username} set to: {password}")
    except User.DoesNotExist:
        print(f"User {username} not found!")

# 1. MySQL
print("--- MySQL ---")
os.environ['USE_SQLITE'] = '0'
django.setup()
set_password('IsabelCGJ', 'AgroSmart2025')

# 2. SQLite (Need to hack the setup or run in subprocess, but since I can't easily tear down django setup...)
# I will create a separate script for SQLite to be safe.

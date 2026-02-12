import os
import django
from django.contrib.auth import get_user_model

# 1. Update MySQL
print("--- Updating MySQL ---")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
os.environ['USE_SQLITE'] = '0'
django.setup()

User = get_user_model()
try:
    user = User.objects.get(username='IsabelCGJ')
    user.set_password('123456789L.')
    user.save()
    print("MySQL: Password restored to '123456789L.'")
except User.DoesNotExist:
    print("MySQL: User not found")

# 2. Update SQLite (just in case)
print("\n--- Updating SQLite ---")
# Resetting setup isn't clean in one script, so we rely on the previous run or separate script. 
# But let's try to just run a shell command for the second part to be safe.

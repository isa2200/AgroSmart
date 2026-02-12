import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Force SQLite settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.dev'
os.environ['USE_SQLITE'] = '1'

try:
    django.setup()
    from django.contrib.auth.models import User
    
    print("Checking SQLite database...")
    user = User.objects.filter(username='IsabelCGJ').first()
    if user:
        print(f"User 'IsabelCGJ' found in SQLite. Resetting password...")
        user.set_password('admin123')
        user.save()
        print("Password reset in SQLite.")
    else:
        print("User 'IsabelCGJ' NOT found in SQLite.")
        print("Users in SQLite:", [u.username for u in User.objects.all()])

except Exception as e:
    print(f"Error: {e}")

import os
import django
from django.contrib.auth import get_user_model
from django.conf import settings

def update_user_in_current_db(db_name_label):
    User = get_user_model()
    username = 'IsabelCGJ'
    password = '123456789L.'
    
    print(f"--- Checking {db_name_label} ---")
    try:
        # Check if user exists
        try:
            user = User.objects.get(username=username)
            print(f"User {username} found.")
        except User.DoesNotExist:
            print(f"User {username} not found. Creating...")
            user = User.objects.create_user(username=username, email='isabel@example.com')
        
        # Update attributes
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"User {username} updated: Active=True, Staff=True, Superuser=True, Password set.")
        
        # Verify
        if user.check_password(password):
            print("Password verification SUCCESS.")
        else:
            print("Password verification FAILED.")
            
    except Exception as e:
        print(f"Error updating {db_name_label}: {e}")

# 1. Update MySQL (Current Default)
print("Configuring for MySQL (default)...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
# Ensure USE_SQLITE is 0 for MySQL check
os.environ['USE_SQLITE'] = '0'
django.setup()

print(f"Current DB Engine: {settings.DATABASES['default']['ENGINE']}")
update_user_in_current_db("MySQL")

# 2. Update SQLite (For legacy/cached server instances)
print("\nConfiguring for SQLite...")
# We need to reset django to switch databases in the same script, 
# but Django doesn't support full teardown/setup easily in one script run without hacks.
# Instead, I will spawn a subprocess or just trust the first part and run a second script for SQLite.

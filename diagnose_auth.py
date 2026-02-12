import os
import django
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

# Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
# Force MySQL first
os.environ['USE_SQLITE'] = '0'
django.setup()

User = get_user_model()
username = 'IsabelCGJ'
password = '123456789L.'

print(f"--- Diagnosing Authentication for {username} ---")
print(f"DB Engine: {settings.DATABASES['default']['ENGINE']}")

try:
    user = User.objects.get(username=username)
    print(f"User found: {user.username} (pk={user.pk})")
    print(f"User is_active: {user.is_active}")
    print(f"User has usable password: {user.has_usable_password()}")
    print(f"Password hash: {user.password[:20]}...")
    
    # Test check_password directly
    is_correct = user.check_password(password)
    print(f"check_password('{password}') returned: {is_correct}")
    
    # Test authenticate()
    print("Attempting authenticate()...")
    auth_user = authenticate(username=username, password=password)
    if auth_user:
        print("authenticate() SUCCESS! User returned.")
    else:
        print("authenticate() FAILED! Returned None.")
        
except User.DoesNotExist:
    print("User NOT found in DB.")


import os
import django
from django.conf import settings
from django.contrib.auth import authenticate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

print(f"DEBUG: {settings.DEBUG}")
print(f"DATABASES: {settings.DATABASES['default']['ENGINE']} - {settings.DATABASES['default']['NAME']}")
print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'IsabelCGJ'
try:
    user = User.objects.get(username=username)
    print(f"User '{username}' found.")
    print(f"User has usable password: {user.has_usable_password()}")
    
    # Check passwords
    if user.check_password('123456789L.'):
        print("Password is '123456789L.'")
    elif user.check_password('admin123'):
        print("Password is 'admin123'")
    else:
        print("Password is neither '123456789L.' nor 'admin123'")
        
    # Check profile
    if hasattr(user, 'perfilusuario'):
        print(f"Profile role: {user.perfilusuario.rol}")
    else:
        print("No profile found for user.")
        
except User.DoesNotExist:
    print(f"User '{username}' does not exist.")

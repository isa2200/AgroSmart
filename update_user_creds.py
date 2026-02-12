import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

User = get_user_model()
username = 'IsabelCGJ'

try:
    user = User.objects.get(username=username)
    print(f"Updating user '{username}'...")
    
    # Update password to admin123
    user.set_password('admin123')
    user.save()
    print("Password updated to 'admin123'.")
    
    # Update profile to superusuario
    if hasattr(user, 'perfilusuario'):
        profile = user.perfilusuario
        profile.rol = 'superusuario'
        profile.save()
        print("Profile role updated to 'superusuario'.")
    else:
        print("No profile found to update.")

except User.DoesNotExist:
    print(f"User '{username}' does not exist.")

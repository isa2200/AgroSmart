
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from apps.usuarios.models import PerfilUsuario

User = get_user_model()
username = 'IsabelCGJ'
password = '123456789L'

try:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"User found: {user.username}")
        print(f"Is active: {user.is_active}")
        print(f"Is staff: {user.is_staff}")
        print(f"Is superuser: {user.is_superuser}")
        
        # Check password
        check = user.check_password(password)
        print(f"Password check for '{password}': {check}")
        
        # Reset again just in case
        user.set_password(password)
        user.is_active = True  # Ensure active
        user.save()
        print(f"Password reset and saved again.")
        
        # Check password again
        check_after = user.check_password(password)
        print(f"Password check after reset: {check_after}")

    else:
        print(f"User {username} NOT found.")

except Exception as e:
    print(f"Error: {e}")


import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def setup_user():
    username = 'IsabelCGJ'
    email = 'isabel@example.com'
    password = '123456789L.'
    
    try:
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            print(f"User {username} updated successfully.")
        else:
            User.objects.create_superuser(username, email, password)
            print(f"User {username} created successfully.")
            
    except Exception as e:
        print(f"Error setting up user: {e}")

if __name__ == '__main__':
    setup_user()

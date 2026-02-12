import os
import django
import sys

sys.path.append(os.getcwd())
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.dev'
os.environ['USE_SQLITE'] = '1'

try:
    django.setup()
    from django.contrib.auth import authenticate
    from django.contrib.auth.models import User
    
    username = 'IsabelCGJ'
    password = 'admin123'
    
    print(f"Checking user: {username}")
    user = User.objects.filter(username=username).first()
    
    if user:
        print(f"User found: ID={user.id}, Active={user.is_active}, Superuser={user.is_superuser}")
        print(f"Password hash: {user.password[:20]}...")
        
        # Try authenticate
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            print("Authentication SUCCESSFUL!")
        else:
            print("Authentication FAILED.")
            # Try setting password again
            print("Resetting password again to ensure match...")
            user.set_password(password)
            user.save()
            
            # Retry
            auth_user_retry = authenticate(username=username, password=password)
            if auth_user_retry:
                print("Authentication SUCCESSFUL after reset.")
            else:
                print("Authentication FAILED even after reset.")
    else:
        print("User NOT found.")
        
except Exception as e:
    print(f"Error: {e}")

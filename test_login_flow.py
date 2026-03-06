import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Setup environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
sys.path.append(os.getcwd())
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

from django.contrib.auth.models import User

def test_login():
    print("--- Starting Login Flow Diagnosis ---")
    
    # 1. Verify User
    username = 'IsabelCGJ'
    password = '123456789L.'
    
    try:
        user = User.objects.get(username=username)
        print(f"User found: {user.username}")
        print(f"Active: {user.is_active}")
        print(f"Check Password: {user.check_password(password)}")
        
        if not user.check_password(password):
            print("CRITICAL: Password check failed directly on model!")
            print("Resetting password...")
            user.set_password(password)
            user.save()
            print(f"Password check after reset: {user.check_password(password)}")
            
    except User.DoesNotExist:
        print(f"CRITICAL: User {username} does not exist!")
        return

    # 2. Test Client Login
    client = Client()
    login_url = reverse('usuarios:login')
    print(f"Login URL: {login_url}")
    
    # Get the login page first (to get CSRF cookie)
    response = client.get(login_url)
    print(f"GET Login Page: {response.status_code}")
    
    # Post credentials
    print(f"Attempting POST to {login_url}...")
    response = client.post(login_url, {
        'username': username,
        'password': password
    }, follow=True)
    
    print(f"POST Response Status: {response.status_code}")
    print(f"Redirect Chain: {response.redirect_chain}")
    
    # Check if we are logged in
    is_logged_in = '_auth_user_id' in client.session
    print(f"Session Logged In: {is_logged_in}")
    
    if is_logged_in:
        print("LOGIN SUCCESSFUL via Test Client.")
    else:
        print("LOGIN FAILED via Test Client.")
        # Check for form errors in context
        if 'form' in response.context:
            form = response.context['form']
            print(f"Form Errors: {form.errors}")
            print(f"Form Non-Field Errors: {form.non_field_errors()}")
            
            # Print messages
            messages = list(response.context['messages'])
            for m in messages:
                print(f"Message: {m}")

if __name__ == "__main__":
    test_login()

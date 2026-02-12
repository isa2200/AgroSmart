import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

User = get_user_model()
username = 'IsabelCGJ'
new_password = '123456789L.'

try:
    user = User.objects.get(username=username)
    print(f"Found user '{username}'.")
    
    # Update password
    user.set_password(new_password)
    user.save()
    print(f"Password for '{username}' has been updated to '{new_password}'.")
    
    # Verify
    if user.check_password(new_password):
        print("Verification: Password matches.")
    else:
        print("Verification: Password mismatch!")

except User.DoesNotExist:
    print(f"User '{username}' does not exist.")

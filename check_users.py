import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth.models import User

def check_users():
    print("Checking users...")
    users = User.objects.all()
    if not users.exists():
        print("No users found! Creating superuser 'admin' with password 'admin123'")
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    else:
        print(f"Found {users.count()} users:")
        for u in users:
            print(f"- {u.username} (Active: {u.is_active}, Superuser: {u.is_superuser})")
            # Optional: Reset admin password to ensure we know it
            if u.username == 'admin':
                print("Resetting 'admin' password to 'admin123'")
                u.set_password('admin123')
                u.save()

if __name__ == "__main__":
    check_users()

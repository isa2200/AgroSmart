import os
import django
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
os.environ['USE_SQLITE'] = '0'
os.environ['DB_NAME'] = 'AgroSmart'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = 'admin123'
os.environ['DB_HOST'] = '127.0.0.1'
os.environ['DB_PORT'] = '3306'

django.setup()

print(f"Attempting connection to {os.environ['DB_HOST']}:{os.environ['DB_PORT']} as {os.environ['DB_USER']}")

try:
    c = connections['default']
    c.cursor()
    print("SUCCESS: Connected to MySQL database 'AgroSmart'")
except OperationalError as e:
    print(f"FAILURE: Could not connect. Error: {e}")
except Exception as e:
    print(f"ERROR: {e}")

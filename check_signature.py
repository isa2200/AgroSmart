import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.porcinos.models import BitacoraDiariaPorcinos

try:
    b = BitacoraDiariaPorcinos.objects.last()
    if b:
        print(f"ID: {b.id}")
        print(f"Firma: {b.firma_encargado}")
        if b.firma_encargado:
            print(f"URL: {b.firma_encargado.url}")
            print(f"Path: {b.firma_encargado.path}")
            print(f"File exists: {os.path.exists(b.firma_encargado.path)}")
        else:
            print("No signature uploaded.")
    else:
        print("No bitacoras found.")
except Exception as e:
    print(f"Error: {e}")

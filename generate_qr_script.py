import os
import django
import qrcode
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

# QR Code Content (Visitor Registration URL)
# In production, change this to the actual domain
url = 'http://127.0.0.1:8000/usuarios/registro-visitante/'

# Generate QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

# Save to static/img
path = os.path.join(settings.BASE_DIR, 'static', 'img', 'qr_visitante_acceso.png')
os.makedirs(os.path.dirname(path), exist_ok=True)
img.save(path)
print(f"QR Code generated and saved to: {path}")

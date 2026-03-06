
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.cunicultura.models import LibroDiarioConejos
from apps.cunicultura.forms import LibroDiarioConejosForm

def verify():
    print("Verifying LibroDiarioConejos model fields...")
    model_fields = [f.name for f in LibroDiarioConejos._meta.get_fields()]
    required_fields = ['alimentacion_am', 'alimentacion_pm', 'alimentacion_total']
    
    for field in required_fields:
        if field in model_fields:
            print(f"✅ Field '{field}' exists in model.")
        else:
            print(f"❌ Field '{field}' MISSING in model.")

    print("\nVerifying LibroDiarioConejosForm fields...")
    form = LibroDiarioConejosForm()
    form_fields = form.fields.keys()
    
    for field in required_fields:
        if field in form_fields:
            print(f"✅ Field '{field}' exists in form.")
            widget = form.fields[field].widget
            attrs = widget.attrs
            print(f"   Widget attrs: {attrs}")
        else:
            print(f"❌ Field '{field}' MISSING in form.")

if __name__ == '__main__':
    verify()

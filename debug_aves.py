
import os
import django
from django.conf import settings
from django.utils import timezone
import sys

# Setup Django environment
sys.path.append('c:/Users/ISABEL/Documents/AgroSmart')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.aves.models import LoteAves, BitacoraDiaria

print("Checking LoteAves...")
lotes = LoteAves.objects.all()
for lote in lotes:
    print(f"Lote: {lote.codigo}, Active: {lote.is_active}, Estado: {lote.estado}, Aves Actual: {lote.numero_aves_actual}")

print("\nChecking BitacoraDiaria (Last 5)...")
bitacoras = BitacoraDiaria.objects.order_by('-fecha')[:5]
for b in bitacoras:
    print(f"Date: {b.fecha}, Lote: {b.lote.codigo}, Produccion: {b.produccion_total}, Mortalidad: {b.mortalidad}")

print(f"\nToday is: {timezone.now().date()}")

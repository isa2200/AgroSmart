import os
import django
import json
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Avg

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.porcinos.models import LotePorcino, BitacoraDiariaPorcinos

def test_dashboard_logic():
    print("Testing dashboard logic...")
    
    # Simulate the query logic
    lotes_qs = LotePorcino.objects.filter(is_active=True)
    
    # 1. Test Aggregations
    total_cerdos = lotes_qs.aggregate(total=Sum('numero_cerdos_actual'))['total'] or 0
    print(f"Total cerdos: {total_cerdos} (type: {type(total_cerdos)})")
    
    hoy = timezone.now().date()
    registros_qs = BitacoraDiariaPorcinos.objects.select_related('lote').filter(lote__in=lotes_qs)
    
    mortalidad_hoy = registros_qs.filter(fecha=hoy).aggregate(total=Sum('mortalidad'))['total'] or 0
    print(f"Mortalidad hoy: {mortalidad_hoy} (type: {type(mortalidad_hoy)})")
    
    # 2. Test Loop Logic
    desde_30d = hoy - timezone.timedelta(days=29)
    rango_fechas = [desde_30d + timezone.timedelta(days=i) for i in range(30)]
    
    evolucion_peso = []
    
    for fecha in rango_fechas:
        regs = registros_qs.filter(fecha=fecha)
        
        # Peso promedio
        val_peso = regs.aggregate(prom=Avg('peso_promedio'))['prom']
        peso_prom = float(val_peso) if val_peso is not None else 0.0
        
        evolucion_peso.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'peso_promedio': round(peso_prom, 2)
        })

    # 3. Test JSON Serialization
    try:
        json_output = json.dumps(evolucion_peso)
        print("JSON serialization SUCCESS")
        # print(json_output[:100])
    except Exception as e:
        print(f"JSON serialization FAILED: {e}")

if __name__ == "__main__":
    test_dashboard_logic()

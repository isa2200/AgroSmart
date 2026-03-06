import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.cunicultura.models import InventarioConejos

def populate_inventario():
    # Clear existing data to match the user's manual record exactly
    print("Limpiando registros existentes...")
    InventarioConejos.objects.all().delete()
    
    data = [
        {
            "fecha": "2025-11-12", "detalle": "Parto Jaula #1", "madre_id": "769",
            "gazapos_vivos": 7, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 3, "hembra_levante_ceba": 1, "reproductores": 15, "hembra_reemplazo": 3, "hembra_no_lactando": 47, "hembra_lactando": 1, "gazapos": 7
        },
        {
            "fecha": "2025-11-14", "detalle": "Parto Jaula #23", "madre_id": None,
            "gazapos_vivos": 2, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 3, "hembra_levante_ceba": 1, "reproductores": 15, "hembra_reemplazo": 3, "hembra_no_lactando": 46, "hembra_lactando": 2, "gazapos": 9
        },
        {
            "fecha": "2025-11-14", "detalle": "Parto Jaula #41", "madre_id": None,
            "gazapos_vivos": 1, "gazapos_muertos": 9, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 3, "hembra_levante_ceba": 1, "reproductores": 15, "hembra_reemplazo": 3, "hembra_no_lactando": 45, "hembra_lactando": 3, "gazapos": 10
        },
        {
            "fecha": "2025-11-16", "detalle": "Muerte 1 gazapo Jaula #41", "madre_id": None,
            "gazapos_vivos": 0, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 1,
            "macho_levante_ceba": 3, "hembra_levante_ceba": 1, "reproductores": 15, "hembra_reemplazo": 3, "hembra_no_lactando": 46, "hembra_lactando": 2, "gazapos": 9
        },
        {
            "fecha": "2025-11-17", "detalle": "Se pasan 3 hembras de Reemplazo a Reproductor", "madre_id": None,
            "gazapos_vivos": 0, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 3, "hembra_levante_ceba": 1, "reproductores": 15, "hembra_reemplazo": 0, "hembra_no_lactando": 49, "hembra_lactando": 2, "gazapos": 9
        },
        {
            "fecha": "2025-11-28", "detalle": "Venta 1 Macho de Levante y Ceba", "madre_id": None,
            "gazapos_vivos": 0, "gazapos_muertos": 0, "compra": 0, "venta": 1, "muerte": 0,
            "macho_levante_ceba": 2, "hembra_levante_ceba": 1, "reproductores": 15, "hembra_reemplazo": 0, "hembra_no_lactando": 49, "hembra_lactando": 2, "gazapos": 9
        },
        {
            "fecha": "2025-11-30", "detalle": "Se pasa 1 Macho de L y C a Reproductor", "madre_id": None,
            "gazapos_vivos": 0, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 49, "hembra_lactando": 2, "gazapos": 9
        },
        {
            "fecha": "2025-12-03", "detalle": "Parto Jaula #20", "madre_id": "801",
            "gazapos_vivos": 9, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 48, "hembra_lactando": 3, "gazapos": 18
        },
        {
            "fecha": "2025-12-05", "detalle": "Parto Jaula #22", "madre_id": "738",
            "gazapos_vivos": 5, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 47, "hembra_lactando": 4, "gazapos": 23
        },
        {
            "fecha": "2025-12-06", "detalle": "Parto Jaula #27", "madre_id": "667",
            "gazapos_vivos": 8, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 46, "hembra_lactando": 5, "gazapos": 31
        },
        {
            "fecha": "2025-12-07", "detalle": "Parto Jaula #39", "madre_id": "720",
            "gazapos_vivos": 6, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 45, "hembra_lactando": 6, "gazapos": 37
        },
        {
            "fecha": "2025-12-08", "detalle": "Muerte 1 gazapo Jaula #39", "madre_id": None,
            "gazapos_vivos": 0, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 1,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 45, "hembra_lactando": 6, "gazapos": 36
        },
        {
            "fecha": "2025-12-14", "detalle": "Parto Jaula #2", "madre_id": "4004",
            "gazapos_vivos": 2, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 44, "hembra_lactando": 7, "gazapos": 38
        },
        {
            "fecha": "2025-12-16", "detalle": "Parto Jaula #16", "madre_id": "848",
            "gazapos_vivos": 7, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 43, "hembra_lactando": 8, "gazapos": 45
        },
        {
            "fecha": "2025-12-16", "detalle": "Parto Jaula #61", "madre_id": "833",
            "gazapos_vivos": 8, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 42, "hembra_lactando": 9, "gazapos": 53
        },
        {
            "fecha": "2025-12-19", "detalle": "Parto Jaula #5", "madre_id": "746",
            "gazapos_vivos": 7, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 41, "hembra_lactando": 10, "gazapos": 60
        },
        {
            "fecha": "2025-12-19", "detalle": "Parto Jaula #46", "madre_id": "103",
            "gazapos_vivos": 3, "gazapos_muertos": 5, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 40, "hembra_lactando": 11, "gazapos": 63
        },
        {
            "fecha": "2025-12-20", "detalle": "Parto Jaula #4", "madre_id": "846",
            "gazapos_vivos": 6, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 1, "hembra_levante_ceba": 1, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 39, "hembra_lactando": 12, "gazapos": 69
        },
        {
            "fecha": "2025-12-20", "detalle": "Destete 2 Reproductores (5M - 4H)", "madre_id": None,
            "gazapos_vivos": 0, "gazapos_muertos": 0, "compra": 0, "venta": 0, "muerte": 0,
            "macho_levante_ceba": 6, "hembra_levante_ceba": 5, "reproductores": 16, "hembra_reemplazo": 0, "hembra_no_lactando": 41, "hembra_lactando": 10, "gazapos": 60
        }
    ]

    print(f"Insertando {len(data)} registros...")
    for item in data:
        InventarioConejos.objects.create(**item)
    
    print("¡Datos insertados correctamente!")

if __name__ == "__main__":
    populate_inventario()

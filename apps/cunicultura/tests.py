from django.test import TestCase
from .models import InventarioConejos

class InventarioConejosTests(TestCase):
    def test_total_calculation(self):
        inventario = InventarioConejos(
            detalle="Test Inventario",
            macho_levante_ceba=10,
            hembra_levante_ceba=15,
            reproductores=5,
            hembra_reemplazo=3,
            hembra_no_lactando=2,
            hembra_lactando=4,
            gazapos=20
        )
        inventario.save()
        
        # Expected total: 10 + 15 + 5 + 3 + 2 + 4 + 20 = 59
        self.assertEqual(inventario.total, 59)

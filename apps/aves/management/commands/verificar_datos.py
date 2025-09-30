from django.core.management.base import BaseCommand
from django.db.models import Sum
from apps.aves.models import BitacoraDiaria, InventarioHuevos, LoteAves


class Command(BaseCommand):
    help = 'Verifica los datos de bitácoras e inventario de huevos'

    def handle(self, *args, **options):
        self.stdout.write('=== VERIFICACIÓN DE DATOS ===\n')
        
        # Verificar bitácoras
        bitacoras = BitacoraDiaria.objects.all()
        self.stdout.write(f'📊 Total de bitácoras registradas: {bitacoras.count()}')
        
        if bitacoras.exists():
            self.stdout.write('\n--- BITÁCORAS ENCONTRADAS ---')
            for bitacora in bitacoras.order_by('-fecha')[:5]:  # Últimas 5
                total_produccion = (
                    bitacora.produccion_aaa + bitacora.produccion_aa + 
                    bitacora.produccion_a + bitacora.produccion_b + bitacora.produccion_c
                )
                self.stdout.write(
                    f'📅 {bitacora.fecha} - Lote: {bitacora.lote.codigo} - '
                    f'Producción total: {total_produccion} huevos'
                )
                self.stdout.write(
                    f'   AAA: {bitacora.produccion_aaa}, AA: {bitacora.produccion_aa}, '
                    f'A: {bitacora.produccion_a}, B: {bitacora.produccion_b}, C: {bitacora.produccion_c}'
                )
        
        # Verificar inventario
        inventarios = InventarioHuevos.objects.all()
        self.stdout.write(f'\n🥚 Total de inventarios: {inventarios.count()}')
        
        if inventarios.exists():
            self.stdout.write('\n--- INVENTARIO ACTUAL ---')
            total_huevos = 0
            for inv in inventarios.order_by('categoria'):
                total_huevos += inv.cantidad_actual
                self.stdout.write(
                    f'Categoría {inv.categoria}: {inv.cantidad_actual} huevos '
                    f'(Mín: {inv.cantidad_minima})'
                )
            self.stdout.write(f'\n🥚 TOTAL DE HUEVOS EN INVENTARIO: {total_huevos}')
        else:
            self.stdout.write('❌ No hay inventarios registrados')
        
        # Verificar lotes
        lotes = LoteAves.objects.filter(is_active=True)
        self.stdout.write(f'\n🐔 Lotes activos: {lotes.count()}')
        
        if lotes.exists():
            self.stdout.write('\n--- LOTES ACTIVOS ---')
            for lote in lotes:
                self.stdout.write(
                    f'Lote {lote.codigo}: {lote.numero_aves_actual} aves - '
                    f'Estado: {lote.estado} - Galpón: {lote.galpon}'
                )
        
        # Calcular totales de producción desde bitácoras
        if bitacoras.exists():
            totales = bitacoras.aggregate(
                total_aaa=Sum('produccion_aaa'),
                total_aa=Sum('produccion_aa'),
                total_a=Sum('produccion_a'),
                total_b=Sum('produccion_b'),
                total_c=Sum('produccion_c'),
            )
            
            total_producido = sum(v or 0 for v in totales.values())
            self.stdout.write(f'\n📈 TOTAL PRODUCIDO SEGÚN BITÁCORAS: {total_producido} huevos')
            
            self.stdout.write('\n--- PRODUCCIÓN POR CATEGORÍA (BITÁCORAS) ---')
            for categoria, total in totales.items():
                categoria_clean = categoria.replace('total_', '').upper()
                self.stdout.write(f'{categoria_clean}: {total or 0} huevos')
        
        self.stdout.write('\n=== FIN DE VERIFICACIÓN ===')
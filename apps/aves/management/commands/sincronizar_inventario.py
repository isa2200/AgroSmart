from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from apps.aves.models import BitacoraDiaria, InventarioHuevos


class Command(BaseCommand):
    help = 'Sincroniza el inventario de huevos con las bitácoras existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resetea completamente el inventario antes de sincronizar',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se haría sin ejecutar los cambios',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Iniciando sincronización del inventario...\n')
        
        # Verificar bitácoras existentes
        bitacoras = BitacoraDiaria.objects.all().order_by('fecha')
        self.stdout.write(f'📊 Bitácoras encontradas: {bitacoras.count()}')
        
        if not bitacoras.exists():
            self.stdout.write(
                self.style.WARNING('❌ No hay bitácoras registradas. No se puede sincronizar.')
            )
            return
        
        # Mostrar estado actual del inventario
        inventarios_actuales = InventarioHuevos.objects.all()
        self.stdout.write(f'🥚 Inventarios actuales: {inventarios_actuales.count()}')
        
        if inventarios_actuales.exists():
            self.stdout.write('\n--- INVENTARIO ACTUAL ---')
            for inv in inventarios_actuales.order_by('categoria'):
                self.stdout.write(f'Categoría {inv.categoria}: {inv.cantidad_actual} huevos')
        
        # Calcular lo que debería ser el inventario
        totales_bitacoras = bitacoras.aggregate(
            total_aaa=Sum('produccion_aaa'),
            total_aa=Sum('produccion_aa'),
            total_a=Sum('produccion_a'),
            total_b=Sum('produccion_b'),
            total_c=Sum('produccion_c'),
        )
        
        inventario_esperado = {
            'AAA': totales_bitacoras['total_aaa'] or 0,
            'AA': totales_bitacoras['total_aa'] or 0,
            'A': totales_bitacoras['total_a'] or 0,
            'B': totales_bitacoras['total_b'] or 0,
            'C': totales_bitacoras['total_c'] or 0,
        }
        
        total_esperado = sum(inventario_esperado.values())
        self.stdout.write(f'\n📈 Total esperado según bitácoras: {total_esperado} huevos')
        
        self.stdout.write('\n--- INVENTARIO ESPERADO ---')
        for categoria, cantidad in inventario_esperado.items():
            self.stdout.write(f'Categoría {categoria}: {cantidad} huevos')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\n🔍 MODO DRY-RUN: No se realizarán cambios')
            )
            return
        
        # Ejecutar sincronización
        with transaction.atomic():
            if options['reset']:
                self.stdout.write('\n🗑️ Eliminando inventario actual...')
                InventarioHuevos.objects.all().delete()
            
            self.stdout.write('\n🔄 Sincronizando inventario...')
            
            for categoria, cantidad_esperada in inventario_esperado.items():
                inventario, created = InventarioHuevos.objects.get_or_create(
                    categoria=categoria,
                    defaults={'cantidad_actual': 0, 'cantidad_minima': 100}
                )
                
                if created:
                    inventario.cantidad_actual = cantidad_esperada
                    self.stdout.write(f'✅ Creado inventario {categoria}: {cantidad_esperada} huevos')
                else:
                    cantidad_anterior = inventario.cantidad_actual
                    inventario.cantidad_actual = cantidad_esperada
                    self.stdout.write(
                        f'🔄 Actualizado inventario {categoria}: {cantidad_anterior} → {cantidad_esperada} huevos'
                    )
                
                inventario.save()
        
        # Mostrar resultado final
        self.stdout.write('\n--- INVENTARIO FINAL ---')
        inventarios_finales = InventarioHuevos.objects.all().order_by('categoria')
        total_final = 0
        
        for inv in inventarios_finales:
            total_final += inv.cantidad_actual
            estado = "⚠️ BAJO" if inv.necesita_reposicion else "✅ OK"
            self.stdout.write(
                f'Categoría {inv.categoria}: {inv.cantidad_actual} huevos - {estado}'
            )
        
        self.stdout.write(f'\n🥚 TOTAL FINAL: {total_final} huevos')
        self.stdout.write(
            self.style.SUCCESS('✅ Sincronización completada exitosamente!')
        )
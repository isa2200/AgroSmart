"""
Comando para actualizar automáticamente los stocks mínimos de huevos
basándose en la cantidad total de gallinas.
"""

from django.core.management.base import BaseCommand
from django.db.models import Sum
from apps.aves.models import InventarioHuevos, LoteAves


class Command(BaseCommand):
    help = 'Actualiza automáticamente los stocks mínimos de huevos basándose en la cantidad de gallinas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categoria',
            type=str,
            help='Actualizar solo una categoría específica (AAA, AA, A, B, C)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar cambios sin aplicarlos',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar actualización incluso si stock_automatico está desactivado',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Iniciando actualización de stocks mínimos...'))
        
        # Obtener total de gallinas en postura
        total_gallinas = LoteAves.objects.filter(
            is_active=True,
            estado='postura'
        ).aggregate(total=Sum('numero_aves_actual'))['total'] or 0
        
        self.stdout.write(f'📊 Total de gallinas en postura: {total_gallinas}')
        
        if total_gallinas == 0:
            self.stdout.write(self.style.WARNING('⚠️  No hay gallinas en postura activas. No se actualizarán los stocks.'))
            return
        
        # Filtrar inventarios
        inventarios = InventarioHuevos.objects.all()
        if options['categoria']:
            inventarios = inventarios.filter(categoria=options['categoria'].upper())
        
        if not options['force']:
            inventarios = inventarios.filter(stock_automatico=True)
        
        actualizados = 0
        
        for inventario in inventarios:
            stock_anterior = inventario.cantidad_minima
            nuevo_stock = inventario.calcular_stock_minimo_automatico()
            
            if stock_anterior != nuevo_stock:
                self.stdout.write(
                    f'📦 {inventario.categoria}: {stock_anterior} → {nuevo_stock} '
                    f'({"+" if nuevo_stock > stock_anterior else ""}{nuevo_stock - stock_anterior})'
                )
                
                if not options['dry_run']:
                    inventario.cantidad_minima = nuevo_stock
                    inventario.save(update_fields=['cantidad_minima', 'fecha_ultima_actualizacion'])
                    actualizados += 1
            else:
                self.stdout.write(f'✅ {inventario.categoria}: Sin cambios ({stock_anterior})')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('🔍 Modo dry-run: No se aplicaron cambios'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Actualización completada. {actualizados} inventarios actualizados.')
            )
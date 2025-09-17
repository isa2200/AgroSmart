"""
Comando para crear líneas genéticas iniciales.
"""

from django.core.management.base import BaseCommand
from apps.aves.models import LineaGenetica


class Command(BaseCommand):
    help = 'Crear líneas genéticas iniciales para el sistema'
    
    def handle(self, *args, **options):
        lineas_geneticas = [
            {
                'nombre': 'Hy-Line Brown',
                'descripcion': 'Gallinas ponedoras de huevos marrones, alta producción y resistencia',
                'peso_promedio_adulto': 2.0,
                'produccion_estimada_dia': 85
            },
            {
                'nombre': 'Lohmann Brown',
                'descripcion': 'Excelente conversión alimenticia y alta producción de huevos marrones',
                'peso_promedio_adulto': 2.1,
                'produccion_estimada_dia': 88
            },
            {
                'nombre': 'ISA Brown',
                'descripcion': 'Línea robusta con buena adaptabilidad y producción sostenida',
                'peso_promedio_adulto': 1.9,
                'produccion_estimada_dia': 82
            },
            {
                'nombre': 'Hy-Line W-36',
                'descripcion': 'Gallinas ponedoras de huevos blancos, alta eficiencia',
                'peso_promedio_adulto': 1.6,
                'produccion_estimada_dia': 90
            },
            {
                'nombre': 'Lohmann LSL-Lite',
                'descripcion': 'Línea ligera para huevos blancos, excelente persistencia',
                'peso_promedio_adulto': 1.5,
                'produccion_estimada_dia': 87
            },
            {
                'nombre': 'Bovans Brown',
                'descripcion': 'Buena adaptación a diferentes climas, huevos marrones',
                'peso_promedio_adulto': 2.0,
                'produccion_estimada_dia': 84
            }
        ]
        
        created_count = 0
        for linea_data in lineas_geneticas:
            linea, created = LineaGenetica.objects.get_or_create(
                nombre=linea_data['nombre'],
                defaults={
                    'descripcion': linea_data['descripcion'],
                    'peso_promedio_adulto': linea_data['peso_promedio_adulto'],
                    'produccion_estimada_dia': linea_data['produccion_estimada_dia']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada línea genética: {linea.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Ya existe línea genética: {linea.nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n¡Proceso completado! Se crearon {created_count} líneas genéticas.')
        )
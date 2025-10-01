"""
Comando de gestión para crear datos iniciales del módulo avícola.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.aves.models import TipoVacuna


class Command(BaseCommand):
    help = 'Crea datos iniciales para el módulo avícola'

    def add_arguments(self, parser):
        parser.add_argument(
            '--vacunas',
            action='store_true',
            help='Crear tipos de vacunas iniciales',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Eliminar datos existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['vacunas']:
            self.crear_tipos_vacunas(options['reset'])
        
        if not any([options['vacunas']]):
            self.stdout.write(
                self.style.WARNING('Especifica qué datos crear: --vacunas')
            )

    @transaction.atomic
    def crear_tipos_vacunas(self, reset=False):
        """Crear tipos de vacunas iniciales."""
        
        if reset:
            TipoVacuna.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Tipos de vacunas existentes eliminados.')
            )

        vacunas_iniciales = [
            {
                'nombre': 'Newcastle + Bronquitis',
                'laboratorio': 'Laboratorio Veterinario',
                'enfermedad_previene': 'Newcastle y Bronquitis Infecciosa',
                'via_aplicacion': 'Ocular/Nasal',
                'dosis_por_ave': 0.03,
                'intervalo_dias': 21
            },
            {
                'nombre': 'Gumboro',
                'laboratorio': 'Laboratorio Veterinario',
                'enfermedad_previene': 'Enfermedad de Gumboro',
                'via_aplicacion': 'Agua de bebida',
                'dosis_por_ave': 0.02,
                'intervalo_dias': 14
            },
            {
                'nombre': 'Viruela Aviar',
                'laboratorio': 'Laboratorio Veterinario',
                'enfermedad_previene': 'Viruela Aviar',
                'via_aplicacion': 'Punción alar',
                'dosis_por_ave': 0.01,
                'intervalo_dias': None
            },
            {
                'nombre': 'Coriza Infecciosa',
                'laboratorio': 'Laboratorio Veterinario',
                'enfermedad_previene': 'Coriza Infecciosa',
                'via_aplicacion': 'Subcutánea',
                'dosis_por_ave': 0.5,
                'intervalo_dias': 28
            },
            {
                'nombre': 'Salmonella',
                'laboratorio': 'Laboratorio Veterinario',
                'enfermedad_previene': 'Salmonelosis',
                'via_aplicacion': 'Subcutánea',
                'dosis_por_ave': 0.5,
                'intervalo_dias': 21
            },
            {
                'nombre': 'Laringotraqueitis',
                'laboratorio': 'Laboratorio Veterinario',
                'enfermedad_previene': 'Laringotraqueitis Infecciosa',
                'via_aplicacion': 'Ocular',
                'dosis_por_ave': 0.03,
                'intervalo_dias': None
            }
        ]

        creadas = 0
        for vacuna_data in vacunas_iniciales:
            vacuna, created = TipoVacuna.objects.get_or_create(
                nombre=vacuna_data['nombre'],
                defaults=vacuna_data
            )
            if created:
                creadas += 1
                self.stdout.write(
                    f"✓ Creada vacuna: {vacuna.nombre}"
                )
            else:
                self.stdout.write(
                    f"- Ya existe: {vacuna.nombre}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nProceso completado. {creadas} tipos de vacunas creados.'
            )
        )
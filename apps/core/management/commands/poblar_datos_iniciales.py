"""
Comando personalizado para poblar datos iniciales del sistema AgroSmart.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.usuarios.models import PerfilUsuario
from apps.core.models import Lote, Categoria
from apps.aves.models import LoteAves, BitacoraDiaria
from apps.dashboard.models import MetricaGeneral
from apps.reportes.models import TipoReporte
from datetime import date, datetime
import random


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos iniciales para AgroSmart'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Eliminar datos existentes antes de poblar',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Eliminando datos existentes...')
            self.limpiar_datos()
        
        self.stdout.write('Creando grupos y permisos...')
        self.crear_grupos_permisos()
        
        self.stdout.write('Creando usuarios...')
        self.crear_usuarios()
        
        self.stdout.write('Creando categorías y lotes...')
        self.crear_categorias_lotes()
        
        self.stdout.write('Creando animales de ejemplo...')
        self.crear_animales()
        
        self.stdout.write('Creando tipos de reportes...')
        self.crear_tipos_reportes()
        
        self.stdout.write('Creando métricas iniciales...')
        self.crear_metricas_iniciales()
        
        self.stdout.write(
            self.style.SUCCESS('¡Datos iniciales creados exitosamente!')
        )
    
    def limpiar_datos(self):
        """Elimina datos existentes (excepto superusuarios)"""
        User.objects.filter(is_superuser=False).delete()
        Lote.objects.all().delete()
        Categoria.objects.all().delete()
        LoteAves.objects.all().delete()
        BitacoraDiaria.objects.all().delete()  # Cambiar ProduccionHuevos por BitacoraDiaria
        MetricaGeneral.objects.all().delete()
        TipoReporte.objects.all().delete()
    
    def crear_grupos_permisos(self):
        """Crea grupos de usuarios con permisos específicos"""
        # Crear grupos
        admin_group, _ = Group.objects.get_or_create(name='Administradores')
        veterinario_group, _ = Group.objects.get_or_create(name='Veterinarios')
        operario_group, _ = Group.objects.get_or_create(name='Operarios')
        
        # Asignar permisos a grupos
        # Los administradores tienen todos los permisos
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)
        
        # Los veterinarios pueden ver y editar animales y reportes
        vet_permissions = Permission.objects.filter(
            content_type__app_label__in=['aves', 'reportes', 'dashboard']
        )
        veterinario_group.permissions.set(vet_permissions)
        
        # Los operarios solo pueden ver y agregar registros básicos
        operario_permissions = Permission.objects.filter(
            codename__in=['view_loteaves', 'add_bitacoradiaria']  # Cambiar add_produccionhuevos por add_bitacoradiaria
        )
        operario_group.permissions.set(operario_permissions)
    
    def crear_usuarios(self):
        """Crea usuarios de ejemplo"""
        # Usuario administrador
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@agrosmart.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                is_staff=True
            )
            admin_group = Group.objects.get(name='Administradores')
            admin_user.groups.add(admin_group)
            
            PerfilUsuario.objects.create(
                usuario=admin_user,
                telefono='3001234567',
                cargo='Administrador General',
                fecha_ingreso=date.today()
            )
        
        # Usuario veterinario
        if not User.objects.filter(username='veterinario').exists():
            vet_user = User.objects.create_user(
                username='veterinario',
                email='veterinario@agrosmart.com',
                password='vet123',
                first_name='Dr. Carlos',
                last_name='Veterinario'
            )
            vet_group = Group.objects.get(name='Veterinarios')
            vet_user.groups.add(vet_group)
            
            PerfilUsuario.objects.create(
                usuario=vet_user,
                telefono='3007654321',
                cargo='Veterinario Principal',
                fecha_ingreso=date.today()
            )
        
        # Usuario operario
        if not User.objects.filter(username='operario').exists():
            op_user = User.objects.create_user(
                username='operario',
                email='operario@agrosmart.com',
                password='op123',
                first_name='Juan',
                last_name='Operario'
            )
            op_group = Group.objects.get(name='Operarios')
            op_user.groups.add(op_group)
            
            PerfilUsuario.objects.create(
                usuario=op_user,
                telefono='3009876543',
                cargo='Operario de Campo',
                fecha_ingreso=date.today()
            )
    
    def crear_categorias_lotes(self):
        """Crea categorías y lotes de ejemplo"""
        # Categorías
        categorias_data = [
            {'nombre': 'Aves Ponedoras', 'descripcion': 'Gallinas para producción de huevos'},
            {'nombre': 'Aves de Engorde', 'descripcion': 'Pollos para engorde y venta'},
        ]
        
        for cat_data in categorias_data:
            Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={'descripcion': cat_data['descripcion']}
            )
        
        # Lotes
        lotes_data = [
            {'nombre': 'Galpón 1 - Aves', 'ubicacion': 'Zona Este', 'capacidad_maxima': 200},
            {'nombre': 'Galpón 2 - Aves', 'ubicacion': 'Zona Oeste', 'capacidad_maxima': 150},
        ]
        
        for lote_data in lotes_data:
            Lote.objects.get_or_create(
                nombre=lote_data['nombre'],
                defaults={
                    'ubicacion': lote_data['ubicacion'],
                    'capacidad_maxima': lote_data['capacidad_maxima']
                }
            )
    
    def crear_animales(self):
        """Crea animales de ejemplo"""
        # Obtener lotes y categorías
        # Crear aves
        galpon1 = Lote.objects.get(nombre='Galpón 1 - Aves')
        galpon2 = Lote.objects.get(nombre='Galpón 2 - Aves')
        cat_ponedoras = Categoria.objects.get(nombre='Aves Ponedoras')
        cat_engorde_aves = Categoria.objects.get(nombre='Aves de Engorde')
        
        lineas_aves = ['Rhode Island Red', 'Leghorn', 'Plymouth Rock', 'Sussex']
        for i in range(1, 51):
            Ave.objects.get_or_create(
                identificacion=f'A{i:03d}',
                defaults={
                    'linea': random.choice(lineas_aves),
                    'sexo': 'H' if i <= 30 else 'M',
                    'fecha_nacimiento': date(2023, random.randint(6, 12), random.randint(1, 28)),
                    'peso_actual': random.uniform(1.5, 2.5),
                    'lote': galpon1 if i <= 25 else galpon2,
                    'categoria': cat_ponedoras if i <= 30 else cat_engorde_aves,
                    'estado_salud': 'saludable',
                    'observaciones': f'Ave número {i}'
                }
            )
    def crear_tipos_reportes(self):
        """Crea tipos de reportes disponibles"""
        tipos_reportes = [
            {
                'nombre': 'Inventario de Animales',
                'descripcion': 'Reporte completo del inventario de todos los animales',
                'categoria': 'inventario'
            },
            {
                'nombre': 'Producción Mensual',
                'descripcion': 'Reporte de producción mensual por tipo de animal',
                'categoria': 'produccion'
            },
            {
                'nombre': 'Estado de Salud',
                'descripcion': 'Reporte del estado de salud de los animales',
                'categoria': 'salud'
            },
            {
                'nombre': 'Análisis Financiero',
                'descripcion': 'Reporte de análisis financiero y costos',
                'categoria': 'financiero'
            },
        ]
        
        for tipo_data in tipos_reportes:
            TipoReporte.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults={
                    'descripcion': tipo_data['descripcion'],
                    'categoria': tipo_data['categoria']
                }
            )
    
    def crear_metricas_iniciales(self):
        """Crea métricas iniciales para el dashboard"""
        metricas_data = [

            {
                'nombre': 'Total Aves',
                'valor': LoteAves.objects.count(),
                'tipo_metrica': 'contador',
                'descripcion': 'Número total de aves en la granja'
            },
            {
                'nombre': 'Producción Huevos Diaria',
                'valor': random.randint(150, 200),
                'tipo_metrica': 'produccion',
                'descripcion': 'Producción diaria promedio de huevos'
            },
        ]
        
        for metrica_data in metricas_data:
            MetricaGeneral.objects.get_or_create(
                nombre=metrica_data['nombre'],
                defaults={
                    'valor': metrica_data['valor'],
                    'tipo_metrica': metrica_data['tipo_metrica'],
                    'descripcion': metrica_data['descripcion']
                }
            )
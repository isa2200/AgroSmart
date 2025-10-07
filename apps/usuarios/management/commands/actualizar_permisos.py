"""
Comando de gestión para actualizar permisos de usuarios.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.usuarios.models import PerfilUsuario
from apps.aves.models import LoteAves


class Command(BaseCommand):
    help = 'Actualiza los permisos de usuarios según sus roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Actualizar solo un usuario específico',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando actualización de permisos...')
        )
        
        # Obtener el ContentType para LoteAves
        content_type = ContentType.objects.get_for_model(LoteAves)
        
        # Crear permisos si no existen
        permisos_lote = [
            ('add_loteaves', 'Can add lote aves'),
            ('change_loteaves', 'Can change lote aves'),
            ('delete_loteaves', 'Can delete lote aves'),
            ('view_loteaves', 'Can view lote aves'),
        ]
        
        for codename, name in permisos_lote:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            if created:
                self.stdout.write(f"Permiso creado: {name}")
        
        # Filtrar usuarios si se especifica uno
        if options['usuario']:
            try:
                user = User.objects.get(username=options['usuario'])
                perfiles = [user.perfilusuario]
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuario {options["usuario"]} no encontrado')
                )
                return
        else:
            perfiles = PerfilUsuario.objects.all()
        
        # Actualizar permisos para cada usuario
        usuarios_actualizados = 0
        for perfil in perfiles:
            user = perfil.user
            self.stdout.write(f"Actualizando: {user.username} (rol: {perfil.rol})")
            
            # Limpiar grupos existentes
            user.groups.clear()
            
            if perfil.rol == 'superusuario':
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(f"  ✓ Configurado como superusuario")
                
            elif perfil.rol == 'admin_aves':
                # Crear grupo para admin_aves
                group, created = Group.objects.get_or_create(name='Administradores_Aves')
                
                # Asignar todos los permisos de LoteAves
                for codename, _ in permisos_lote:
                    permission = Permission.objects.get(
                        codename=codename,
                        content_type=content_type
                    )
                    group.permissions.add(permission)
                
                user.groups.add(group)
                self.stdout.write(f"  ✓ Permisos de admin_aves asignados")
                
            elif perfil.rol == 'solo_vista':
                # Crear grupo para solo_vista
                group, created = Group.objects.get_or_create(name='Solo_Vista')
                
                # Solo permiso de vista
                permission = Permission.objects.get(
                    codename='view_loteaves',
                    content_type=content_type
                )
                group.permissions.add(permission)
                user.groups.add(group)
                self.stdout.write(f"  ✓ Permisos de solo_vista asignados")
            
            usuarios_actualizados += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Actualización completada. {usuarios_actualizados} usuarios procesados.'
            )
        )
        
        # Mostrar resumen
        self.stdout.write('\n📋 RESUMEN DE PERMISOS:')
        for perfil in perfiles:
            user = perfil.user
            permisos = user.get_all_permissions()
            permisos_lote = [p for p in permisos if 'loteaves' in p]
            self.stdout.write(f"\n👤 {user.username} ({perfil.rol}):")
            if user.is_superuser:
                self.stdout.write("  - SUPERUSUARIO (todos los permisos)")
            else:
                for permiso in permisos_lote:
                    self.stdout.write(f"  - {permiso}")
                if not permisos_lote:
                    self.stdout.write("  - Sin permisos específicos de lotes")
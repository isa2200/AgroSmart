"""
Señales para la app de usuarios.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se crea un usuario."""
    if created:
        # Verificar si ya existe un perfil para este usuario
        if not hasattr(instance, 'perfilusuario'):
            try:
                # Usar un identificador único temporal para evitar conflictos
                import uuid
                temp_cedula = f'temp_{uuid.uuid4().hex[:8]}'
                
                PerfilUsuario.objects.create(
                    user=instance,
                    rol='solo_vista',
                    cedula=temp_cedula
                )
            except Exception as e:
                # Si hay algún error, no crear el perfil automáticamente
                pass


@receiver(post_save, sender=PerfilUsuario)
def asignar_grupos_permisos(sender, instance, **kwargs):
    """Asigna grupos y permisos basados en el rol del usuario."""
    user = instance.user
    
    # Limpiar grupos existentes
    user.groups.clear()
    
    # Asignar grupo según el rol
    if instance.rol == 'superusuario':
        user.is_staff = True
        user.is_superuser = True
        user.save()
    elif instance.rol.startswith('admin_'):
        area = instance.rol.replace('admin_', '')
        group_name = f'Administradores_{area.title()}'
        group, created = Group.objects.get_or_create(name=group_name)
        
        # Asignar permisos específicos para admin_aves
        if instance.rol == 'admin_aves':
            try:
                # Obtener el ContentType para LoteAves
                from apps.aves.models import LoteAves
                content_type = ContentType.objects.get_for_model(LoteAves)
                
                # Obtener o crear los permisos necesarios
                permisos_necesarios = [
                    'add_loteaves',
                    'change_loteaves', 
                    'delete_loteaves',
                    'view_loteaves'
                ]
                
                for codename in permisos_necesarios:
                    permission, created = Permission.objects.get_or_create(
                        codename=codename,
                        content_type=content_type,
                        defaults={'name': f'Can {codename.split("_")[0]} lote aves'}
                    )
                    group.permissions.add(permission)
                    
            except Exception as e:
                print(f"Error asignando permisos a admin_aves: {e}")
        
        user.groups.add(group)
    elif instance.rol == 'solo_vista':
        group, created = Group.objects.get_or_create(name='Solo_Vista')
        
        # Asignar solo permisos de vista
        try:
            from apps.aves.models import LoteAves
            content_type = ContentType.objects.get_for_model(LoteAves)
            
            permission, created = Permission.objects.get_or_create(
                codename='view_loteaves',
                content_type=content_type,
                defaults={'name': 'Can view lote aves'}
            )
            group.permissions.add(permission)
            
        except Exception as e:
            print(f"Error asignando permisos a solo_vista: {e}")
            
        user.groups.add(group)
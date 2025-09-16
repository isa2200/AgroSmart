"""
Señales para la app de usuarios.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
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
        user.groups.add(group)
    elif instance.rol == 'solo_vista':
        group, created = Group.objects.get_or_create(name='Solo_Vista')
        user.groups.add(group)
"""
Modelos para la gestión de usuarios y permisos en AgroSmart.
"""

from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.core.models import BaseModel


class PerfilUsuario(BaseModel):
    """
    Perfil extendido para usuarios del sistema.
    """
    ROLES = [
        ('superusuario', 'Superusuario'),
        ('admin_aves', 'Administrador de Aves'),
        ('solo_vista', 'Solo Vista'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    rol = models.CharField('Rol', max_length=20, choices=ROLES)
    telefono = models.CharField('Teléfono', max_length=15, blank=True)
    cedula = models.CharField('Cédula', max_length=20, unique=True, blank=True, null=True)  # Permitir vacío temporalmente
    fecha_nacimiento = models.DateField('Fecha de nacimiento', null=True, blank=True)
    direccion = models.TextField('Dirección', blank=True)
    foto = models.ImageField('Foto de perfil', upload_to='usuarios/fotos/', blank=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_rol_display()}"
    
    def tiene_acceso_area(self, area):
        """Verifica si el usuario tiene acceso a un área específica."""
        if self.rol == 'superusuario':
            return True
        return f'admin_{area}' == self.rol
    
    def puede_editar(self):
        """Verifica si el usuario puede editar datos."""
        return self.rol != 'solo_vista'


class RegistroAcceso(BaseModel):
    """
    Registro de accesos al sistema para auditoría.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    ip_address = models.GenericIPAddressField('Dirección IP')
    user_agent = models.TextField('User Agent')
    accion = models.CharField('Acción', max_length=100)
    modulo = models.CharField('Módulo', max_length=50)
    
    class Meta:
        verbose_name = 'Registro de Acceso'
        verbose_name_plural = 'Registros de Acceso'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.created_at}"
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
        ('veterinario', 'Veterinario'),
        ('punto_blanco', 'Punto Blanco (Venta)'),
        ('solo_vista', 'Solo Vista'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    rol = models.CharField('Rol', max_length=20, choices=ROLES)
    telefono = models.CharField('Teléfono', max_length=15, blank=True)
    cedula = models.CharField('Cédula', max_length=20, unique=True, blank=True, null=True)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', null=True, blank=True)
    direccion = models.TextField('Dirección', blank=True)
    foto = models.ImageField('Foto de perfil', upload_to='usuarios/fotos/', blank=True)
    
    # Permisos específicos del módulo avícola
    puede_eliminar_registros = models.BooleanField('Puede eliminar registros', default=False)
    acceso_modulo_avicola = models.BooleanField('Acceso módulo avícola', default=False)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_rol_display()}"
    
    def tiene_acceso_area(self, area):
        """Verifica si el usuario tiene acceso a un área específica."""
        if self.rol == 'superusuario':
            return True
        if area == 'aves':
            return self.acceso_modulo_avicola
        return f'admin_{area}' == self.rol
    
    def puede_editar(self):
        """Verifica si el usuario puede editar datos."""
        return self.rol not in ['solo_vista', 'punto_blanco']
    
    def puede_registrar_vacunas(self):
        """Verifica si puede registrar vacunas."""
        return self.rol in ['superusuario', 'veterinario']
    
    def puede_gestionar_vacunacion(self):
        """Verifica si el usuario puede gestionar vacunación."""
        return self.rol in ['superusuario', 'veterinario']
    
    def puede_ver_inventarios(self):
        """Verifica si el usuario puede ver inventarios."""
        return self.rol in ['superusuario', 'admin_aves', 'punto_blanco', 'solo_vista']
    
    def puede_generar_pedidos(self):
        """Verifica si el usuario puede generar pedidos."""
        return self.rol in ['superusuario', 'punto_blanco']
    
    def requiere_justificacion_modificacion(self):
        """Verifica si requiere justificación para modificaciones."""
        return self.rol in ['admin_aves', 'veterinario']


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
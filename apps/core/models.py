"""
Modelos base y utilidades comunes para el proyecto AgroSmart.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de timestamp automáticos.
    """
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """
    Modelo abstracto que proporciona funcionalidad de activación/desactivación.
    """
    is_active = models.BooleanField('Activo', default=True)
    
    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, ActiveModel):
    """
    Modelo base que combina timestamp y funcionalidad de activación.
    """
    class Meta:
        abstract = True


class Lote(BaseModel):
    """
    Modelo para representar lotes de animales.
    """
    nombre = models.CharField('Nombre del lote', max_length=100)
    descripcion = models.TextField('Descripción', blank=True)
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin = models.DateField('Fecha de fin', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return self.nombre
    
    @property
    def esta_activo(self):
        """Verifica si el lote está actualmente activo."""
        hoy = timezone.now().date()
        if self.fecha_fin:
            return self.fecha_inicio <= hoy <= self.fecha_fin
        return self.fecha_inicio <= hoy


class Categoria(BaseModel):
    """
    Modelo para categorías generales del sistema.
    """
    nombre = models.CharField('Nombre', max_length=100)
    descripcion = models.TextField('Descripción', blank=True)
    color = models.CharField('Color (hex)', max_length=7, default='#007bff')
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
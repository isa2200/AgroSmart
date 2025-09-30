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
    
    def save(self, *args, **kwargs):
        """Override save para asegurar que los timestamps usen timezone aware datetimes."""
        if not self.pk and not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


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
        """
        Determina si el lote está activo basado en las fechas.
        """
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy and (self.fecha_fin is None or self.fecha_fin >= hoy)


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
from django.db import models
from apps.core.models import BaseModel
from django.contrib.auth.models import User

class MetricaGeneral(BaseModel):
    """
    Modelo para almacenar métricas generales del sistema
    """
    nombre = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    unidad = models.CharField(max_length=20)
    fecha_calculo = models.DateTimeField(auto_now=True)
    tipo_metrica = models.CharField(max_length=50, choices=[
        ('produccion', 'Producción'),
        ('inventario', 'Inventario'),
        ('financiero', 'Financiero'),
        ('salud', 'Salud Animal')
    ])
    
    class Meta:
        verbose_name = 'Métrica General'
        verbose_name_plural = 'Métricas Generales'
        ordering = ['-fecha_calculo']

class AlertaSistema(BaseModel):
    """
    Sistema de alertas para el dashboard
    """
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=[
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('success', 'Éxito')
    ], default='info')
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='alertas_dashboard'  # Agregar related_name único
    )
    leida = models.BooleanField(default=False)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Alerta del Sistema'
        verbose_name_plural = 'Alertas del Sistema'
        ordering = ['-created_at']
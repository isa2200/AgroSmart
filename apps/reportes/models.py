"""
Modelos para la gestión de reportes en AgroSmart.
"""

from django.db import models
from apps.core.models import BaseModel
from django.contrib.auth.models import User
from django.utils import timezone

class TipoReporte(BaseModel):
    """
    Tipos de reportes disponibles en el sistema
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50, choices=[
        ('produccion', 'Producción'),
        ('inventario', 'Inventario'),
        ('financiero', 'Financiero'),
        ('salud', 'Salud Animal'),
        ('general', 'General')
    ])
    plantilla_html = models.TextField(blank=True)
    campos_disponibles = models.JSONField(default=dict, help_text="Campos disponibles para el reporte")
    
    class Meta:
        verbose_name = 'Tipo de Reporte'
        verbose_name_plural = 'Tipos de Reportes'
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

class ReporteGenerado(BaseModel):
    """
    Historial de reportes generados
    """
    tipo_reporte = models.ForeignKey(TipoReporte, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_archivo = models.CharField(max_length=255)
    formato = models.CharField(max_length=10, choices=[
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML')
    ])
    parametros = models.JSONField(default=dict, help_text="Parámetros usados para generar el reporte")
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='reportes/', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('generando', 'Generando'),
        ('completado', 'Completado'),
        ('error', 'Error')
    ], default='generando')
    mensaje_error = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.tipo_reporte.nombre} - {self.fecha_generacion.strftime('%d/%m/%Y %H:%M')}"

class ReporteProgramado(BaseModel):
    """
    Reportes programados para generación automática
    """
    tipo_reporte = models.ForeignKey(TipoReporte, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    frecuencia = models.CharField(max_length=20, choices=[
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral')
    ])
    hora_ejecucion = models.TimeField()
    dia_semana = models.IntegerField(null=True, blank=True, help_text="1=Lunes, 7=Domingo")
    dia_mes = models.IntegerField(null=True, blank=True, help_text="Día del mes (1-31)")
    parametros = models.JSONField(default=dict)
    formato_salida = models.CharField(max_length=10, choices=[
        ('excel', 'Excel'),
        ('csv', 'CSV')
    ], default='excel')
    enviar_email = models.BooleanField(default=False)
    emails_destino = models.JSONField(default=list, help_text="Lista de emails para envío")
    ultima_ejecucion = models.DateTimeField(null=True, blank=True)
    proxima_ejecucion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Reporte Programado'
        verbose_name_plural = 'Reportes Programados'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_frecuencia_display()})"
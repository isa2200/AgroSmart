from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import BaseModel


class LotePorcino(BaseModel):
    ESTADOS = [
        ('activo', 'Activo'),
        ('engorde', 'Engorde'),
        ('vendido', 'Vendido'),
        ('cerrado', 'Cerrado'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    corral = models.CharField(max_length=100)
    procedencia = models.CharField(max_length=200, blank=True)
    numero_cerdos_inicial = models.PositiveIntegerField()
    numero_cerdos_actual = models.PositiveIntegerField()
    fecha_llegada = models.DateField()
    peso_total_llegada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    peso_promedio_llegada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_llegada']
        verbose_name = 'Lote de Porcinos'
        verbose_name_plural = 'Lotes de Porcinos'

    def __str__(self):
        return f"{self.codigo} - {self.corral}"

    @property
    def edad_dias(self):
        return (timezone.now().date() - self.fecha_llegada).days


class BitacoraDiariaPorcinos(BaseModel):
    lote = models.ForeignKey(LotePorcino, on_delete=models.CASCADE)
    fecha = models.DateField()
    peso_promedio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    consumo_alimento_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    animales_enfermos = models.PositiveIntegerField(default=0)
    mortalidad = models.PositiveIntegerField(default=0)
    tratamiento_aplicado = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Bitácora Diaria Porcinos'
        verbose_name_plural = 'Bitácoras Diarias Porcinos'

    def __str__(self):
        return f"{self.lote.codigo} {self.fecha}"

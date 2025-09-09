"""
Modelos para la gestión de gallinas ponedoras en AgroSmart.
Enfocado en producción de huevos y gestión sanitaria.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import BaseModel
from apps.core.utils import validar_fecha_no_futura
from django.core.validators import MinValueValidator, MaxValueValidator

# CHOICES PARA MODELOS
LINEA_CHOICES = [
    ('hy_line_brown', 'Hy-Line Brown'),
    ('hy_line_white', 'Hy-Line White'),
    ('lohmann_brown', 'Lohmann Brown'),
    ('isa_brown', 'ISA Brown'),
    ('bovans_brown', 'Bovans Brown'),
    ('otra', 'Otra'),
]

ESTADO_CHOICES = [
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
    ('vendido', 'Vendido'),
    ('terminado', 'Terminado'),
]

# LOTES DE AVES (Refinado)
class LoteAves(BaseModel):
    codigo = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre_lote = models.CharField(max_length=100, unique=True)
    linea = models.CharField(max_length=20, choices=LINEA_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin_produccion = models.DateField(null=True, blank=True)
    cantidad_aves = models.PositiveIntegerField()
    cantidad_actual = models.PositiveIntegerField()
    semana_actual = models.PositiveIntegerField(default=1,validators=[MinValueValidator(1), MaxValueValidator(100)])
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    costo_ave_inicial = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    # Campos calculados

    class Meta:
        verbose_name = 'Lote de Aves'
        verbose_name_plural = 'Lotes de Aves'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['linea']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['codigo']),
        ]

    @property
    def mortalidad_porcentaje(self):
        return ((self.cantidad_aves - self.cantidad_actual) / self.cantidad_aves) * 100
    
    @property
    def dias_produccion(self):
        if self.fecha_fin_produccion:
            return (self.fecha_fin_produccion - self.fecha_inicio).days
        return (timezone.now().date() - self.fecha_inicio).days
        
    def calcular_indicadores(self):  # agregado por corrección QA
        """
        Calcula indicadores de producción del lote.
        """
        from django.db.models import Sum, Avg
        
        # Producción total
        produccion_total = self.producciones.aggregate(
            total_huevos=Sum('yumbos') + Sum('extra') + Sum('aa') + Sum('a') + Sum('b') + Sum('c')
        )['total_huevos'] or 0
        
        # Mortalidad total
        mortalidad_total = self.mortalidades.aggregate(
            total_muertas=Sum('cantidad_muertas')
        )['total_muertas'] or 0
        
        # Costos totales
        costos_totales = self.costos.aggregate(
            total_costos=Sum('costos_fijos') + Sum('costos_variables') + Sum('costo_alimento')
        )['total_costos'] or 0
        
        return {
            'produccion_total': produccion_total,
            'mortalidad_total': mortalidad_total,
            'mortalidad_porcentaje': (mortalidad_total / self.cantidad_aves * 100) if self.cantidad_aves > 0 else 0,
            'costos_totales': costos_totales,
            'costo_por_huevo': (costos_totales / produccion_total) if produccion_total > 0 else 0
        }


# ALERTAS SANITARIAS (Nuevo)
class AlertaSanitaria(BaseModel):
    TIPO_CHOICES = [
        ('mortalidad_alta', 'Mortalidad Alta'),
        ('postura_baja', 'Postura Baja'),
        ('peso_bajo', 'Peso Promedio Bajo'),
        ('vacuna_vencida', 'Vacuna Vencida'),
        ('costo_alto', 'Costo Elevado'),
    ]
    
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensaje = models.TextField()
    valor_actual = models.DecimalField(max_digits=10, decimal_places=2)
    valor_umbral = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_deteccion = models.DateTimeField(auto_now_add=True)
    resuelta = models.BooleanField(default=False)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)


class ProduccionHuevos(BaseModel):
    """
    Modelo para registrar la producción diaria/semanal de huevos por categorías.
    """
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE, related_name='producciones', verbose_name='Lote')
    fecha = models.DateField('Fecha de Producción', validators=[validar_fecha_no_futura])
    semana_produccion = models.PositiveIntegerField('Semana de Producción')
    
    # Clasificación de huevos por categorías
    yumbos = models.PositiveIntegerField('Yumbos', default=0)
    extra = models.PositiveIntegerField('Extra', default=0)
    aa = models.PositiveIntegerField('AA', default=0)
    a = models.PositiveIntegerField('A', default=0)
    b = models.PositiveIntegerField('B', default=0)
    c = models.PositiveIntegerField('C', default=0)
    pipo = models.PositiveIntegerField('Pipo', default=0)
    sucios = models.PositiveIntegerField('Sucios', default=0)
    totiados = models.PositiveIntegerField('Totiados', default=0)
    yema = models.PositiveIntegerField('Yema', default=0)
    
    peso_promedio_huevo = models.DecimalField(
    'Peso Promedio por Huevo (g)', 
    max_digits=5, 
    decimal_places=2,
    validators=[MinValueValidator(30), MaxValueValidator(100)]
    )
    numero_aves_produccion = models.PositiveIntegerField('Número de Aves en Producción')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario que Registró')
    observaciones = models.TextField('Observaciones', blank=True)
    
    class Meta:
        verbose_name = 'Producción de Huevos'
        verbose_name_plural = 'Producción de Huevos'
        ordering = ['-fecha']
        unique_together = ['lote', 'fecha']
        indexes = [
            models.Index(fields=['lote', 'fecha']),
            models.Index(fields=['fecha']),
            models.Index(fields=['semana_produccion']),
            models.Index(fields=['lote', 'semana_produccion']),
        ]
    
    def __str__(self):
        return f"{self.lote.nombre_lote} - {self.fecha} ({self.total_huevos} huevos)"
    
    @property
    def total_huevos(self):
        """Calcula el total de huevos producidos."""
        return (self.yumbos + self.extra + self.aa + self.a + self.b + 
                self.c + self.pipo + self.sucios + self.totiados + self.yema)
    
    @property
    def huevos_comerciales(self):
        """Calcula huevos comerciales (excluyendo pipo, sucios, totiados, yema)."""
        return self.yumbos + self.extra + self.aa + self.a + self.b + self.c
    
    @property
    def porcentaje_postura(self):
        """Calcula el porcentaje de postura."""
        if self.numero_aves_produccion > 0:
            return (self.total_huevos / self.numero_aves_produccion) * 100
        return 0
    
    @property
    def gramos_ave_dia(self):
        """Calcula gramos de huevo por ave por día."""
        if self.numero_aves_produccion > 0:
            peso_total = float(self.peso_promedio_huevo) * self.total_huevos
            return peso_total / self.numero_aves_produccion
        return 0


class CostosProduccion(BaseModel):
    """
    Modelo para registrar costos e ingresos de producción.
    """
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE, related_name='costos', verbose_name='Lote')
    fecha = models.DateField('Fecha', validators=[validar_fecha_no_futura])
    periodo = models.CharField('Período', max_length=20, help_text='Ej: Semana 1, Mes 1')
    
    # Costos
    costos_fijos = models.DecimalField('Costos Fijos', max_digits=12, decimal_places=2, default=0)
    costos_variables = models.DecimalField('Costos Variables', max_digits=12, decimal_places=2, default=0)
    gastos_administracion = models.DecimalField('Gastos de Administración', max_digits=12, decimal_places=2, default=0)
    costo_alimento = models.DecimalField('Costo de Alimento', max_digits=12, decimal_places=2, default=0)
    costo_mano_obra = models.DecimalField('Costo Mano de Obra', max_digits=12, decimal_places=2, default=0)
    otros_costos = models.DecimalField('Otros Costos', max_digits=12, decimal_places=2, default=0)
    
    # Ingresos
    ingresos_venta_huevos = models.DecimalField('Ingresos por Venta de Huevos', max_digits=12, decimal_places=2, default=0)
    ingresos_venta_aves = models.DecimalField('Ingresos por Venta de Aves', max_digits=12, decimal_places=2, default=0)
    otros_ingresos = models.DecimalField('Otros Ingresos', max_digits=12, decimal_places=2, default=0)
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario que Registró')
    observaciones = models.TextField('Observaciones', blank=True)
    
    class Meta:
        verbose_name = 'Costos de Producción'
        verbose_name_plural = 'Costos de Producción'
        ordering = ['-fecha']
        unique_together = ['lote', 'fecha', 'periodo']
    
    def __str__(self):
        return f"{self.lote.nombre_lote} - {self.periodo} ({self.fecha})"
    
    @property
    def total_costos(self):
        """Calcula el total de costos."""
        return (self.costos_fijos + self.costos_variables + self.gastos_administracion + 
                self.costo_alimento + self.costo_mano_obra + self.otros_costos)
    
    @property
    def total_ingresos(self):
        """Calcula el total de ingresos."""
        return self.ingresos_venta_huevos + self.ingresos_venta_aves + self.otros_ingresos
    
    @property
    def utilidad_neta(self):
        """Calcula la utilidad neta."""
        return self.total_ingresos - self.total_costos
    
    @property
    def margen_contribucion(self):
        """Calcula el margen de contribución porcentual."""
        if self.total_ingresos > 0:
            return ((self.total_ingresos - self.costos_variables) / self.total_ingresos) * 100
        return 0
    
    @property
    def rentabilidad(self):
        """Calcula la rentabilidad porcentual."""
        if self.total_costos > 0:
            return (self.utilidad_neta / self.total_costos) * 100
        return 0


class CalendarioVacunas(BaseModel):
    """
    Modelo para definir el calendario de vacunación.
    """
    nombre_vacuna = models.CharField('Nombre de la Vacuna', max_length=100)
    dias_post_nacimiento = models.PositiveIntegerField('Días Post-Nacimiento')
    descripcion = models.TextField('Descripción')
    dosis_ml = models.DecimalField('Dosis (ml)', max_digits=6, decimal_places=2)
    via_aplicacion = models.CharField('Vía de Aplicación', max_length=50)
    obligatoria = models.BooleanField('Obligatoria', default=True)
    
    class Meta:
        verbose_name = 'Calendario de Vacunas'
        verbose_name_plural = 'Calendario de Vacunas'
        ordering = ['dias_post_nacimiento']
    
    def __str__(self):
        return f"{self.nombre_vacuna} - Día {self.dias_post_nacimiento}"


class Vacunacion(BaseModel):
    """
    Modelo para registrar vacunaciones aplicadas.
    """
    ESTADO_CHOICES = [
        ('aplicada', 'Aplicada'),
        ('pendiente', 'Pendiente'),
        ('vencida', 'Vencida'),
    ]
    
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE, related_name='vacunaciones', verbose_name='Lote')
    calendario_vacuna = models.ForeignKey(CalendarioVacunas, on_delete=models.CASCADE, verbose_name='Vacuna del Calendario')
    fecha_programada = models.DateField('Fecha Programada')
    fecha_aplicacion = models.DateField('Fecha de Aplicación', null=True, blank=True)
    dosis_aplicada = models.DecimalField('Dosis Aplicada (ml)', max_digits=6, decimal_places=2)
    numero_aves_vacunadas = models.PositiveIntegerField('Número de Aves Vacunadas')
    responsable = models.CharField('Responsable', max_length=100)
    lote_vacuna = models.CharField('Lote de Vacuna', max_length=50, blank=True)
    estado = models.CharField('Estado', max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField('Observaciones', blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario que Registró')
    
    class Meta:
        verbose_name = 'Vacunación'
        verbose_name_plural = 'Vacunaciones'
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f"{self.lote.nombre_lote} - {self.calendario_vacuna.nombre_vacuna} ({self.get_estado_display()})"
    
    @property
    def dias_vencimiento(self):
        """Calcula días hasta vencimiento (negativo si ya venció)."""
        return (self.fecha_programada - timezone.now().date()).days
    
    @property
    def porcentaje_cobertura(self):
        """Calcula el porcentaje de cobertura de vacunación."""
        if self.lote.cantidad_actual > 0:
            return (self.numero_aves_vacunadas / self.lote.cantidad_actual) * 100
        return 0


class Mortalidad(BaseModel):
    """
    Modelo para registrar mortalidad diaria.
    """
    CAUSA_CHOICES = [
        ('enfermedad', 'Enfermedad'),
        ('accidente', 'Accidente'),
        ('estres', 'Estrés'),
        ('depredacion', 'Depredación'),
        ('vejez', 'Vejez'),
        ('desconocida', 'Desconocida'),
        ('otra', 'Otra'),
    ]
    
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE, related_name='mortalidades', verbose_name='Lote')
    fecha = models.DateField('Fecha', validators=[validar_fecha_no_futura])
    cantidad_muertas = models.PositiveIntegerField('Cantidad de Aves Muertas')
    causa = models.CharField('Causa', max_length=15, choices=CAUSA_CHOICES)
    descripcion_causa = models.TextField('Descripción de la Causa', blank=True)
    accion_tomada = models.TextField('Acción Tomada', blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario que Registró')
    
    class Meta:
        verbose_name = 'Mortalidad'
        verbose_name_plural = 'Mortalidades'
        ordering = ['-fecha']
        indexes = [  # agregado por corrección QA
            models.Index(fields=['lote', 'fecha']),
            models.Index(fields=['fecha']),
            models.Index(fields=['causa']),
        ]
    
    def __str__(self):
        return f"{self.lote.nombre_lote} - {self.fecha} ({self.cantidad_muertas} muertas)"
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            # Validar que no exceda la cantidad actual
            if self.cantidad_muertas > self.lote.cantidad_actual:
                raise ValidationError(
                    f'No se pueden registrar {self.cantidad_muertas} muertes. '
                    f'Solo hay {self.lote.cantidad_actual} aves en el lote.'
                )
            
            # Actualizar cantidad actual del lote
            self.lote.cantidad_actual -= self.cantidad_muertas
            self.lote.save()
        
        super().save(*args, **kwargs)


class IndicadorProduccion(BaseModel):
    """
    Modelo para almacenar indicadores calculados de producción.
    """
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE, related_name='indicadores', verbose_name='Lote')
    fecha_calculo = models.DateField('Fecha de Cálculo', auto_now=True)
    semana_produccion = models.PositiveIntegerField('Semana de Producción')
    
    # Indicadores de producción
    porcentaje_postura_promedio = models.DecimalField('% Postura Promedio', max_digits=5, decimal_places=2, default=0)
    huevos_ave_alojada = models.DecimalField('Huevos por Ave Alojada', max_digits=8, decimal_places=2, default=0)
    gramos_ave_dia_promedio = models.DecimalField('Gramos Ave/Día Promedio', max_digits=6, decimal_places=2, default=0)
    peso_huevo_promedio = models.DecimalField('Peso Huevo Promedio (g)', max_digits=5, decimal_places=2, default=0)
    
    # Indicadores financieros
    costo_por_huevo = models.DecimalField('Costo por Huevo', max_digits=8, decimal_places=4, default=0)
    ingreso_por_huevo = models.DecimalField('Ingreso por Huevo', max_digits=8, decimal_places=4, default=0)
    margen_por_huevo = models.DecimalField('Margen por Huevo', max_digits=8, decimal_places=4, default=0)
    
    class Meta:
        verbose_name = 'Indicador de Producción'
        verbose_name_plural = 'Indicadores de Producción'
        ordering = ['-fecha_calculo']
        unique_together = ['lote', 'semana_produccion']
    
    def __str__(self):
        return f"{self.lote.nombre_lote} - Semana {self.semana_produccion}"

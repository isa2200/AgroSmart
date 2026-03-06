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
    firma_encargado = models.ImageField(upload_to='porcinos/firmas/', null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Bitácora Diaria Porcinos'
        verbose_name_plural = 'Bitácoras Diarias Porcinos'

    def __str__(self):
        return f"{self.lote.codigo} {self.fecha}"


class InventarioPorcino(BaseModel):
    fecha = models.DateField(default=timezone.now)
    detalle = models.CharField(max_length=200, blank=True)
    
    # Población
    madre = models.PositiveIntegerField(default=0)
    reproductores = models.PositiveIntegerField(default=0)
    hembras_reemplazo = models.PositiveIntegerField(default=0)
    hembras_gestacion = models.PositiveIntegerField(default=0)
    hembras_lactando = models.PositiveIntegerField(default=0)
    lechones_lactando = models.PositiveIntegerField(default=0)
    preiniciador = models.PositiveIntegerField(default=0)
    levante_ceba = models.PositiveIntegerField(default=0)
    descartes = models.PositiveIntegerField(default=0)
    
    # Producción
    lechones_vivos = models.PositiveIntegerField(default=0)
    lechones_muertos = models.PositiveIntegerField(default=0)
    destetes = models.PositiveIntegerField(default=0)
    
    # Movimientos
    compras = models.PositiveIntegerField(default=0)
    ventas = models.PositiveIntegerField(default=0)
    salidas = models.PositiveIntegerField(default=0)
    muertes = models.PositiveIntegerField(default=0)
    
    total = models.PositiveIntegerField(default=0)
    
    # Firmas
    firma_realizado = models.ImageField(upload_to='porcinos/firmas/inventario/', null=True, blank=True)
    firma_revisado = models.ImageField(upload_to='porcinos/firmas/inventario/', null=True, blank=True)
    firma_aprobado = models.ImageField(upload_to='porcinos/firmas/inventario/', null=True, blank=True)
    
    realizado_por = models.CharField(max_length=100, blank=True)
    revisado_por = models.CharField(max_length=100, blank=True)
    aprobado_por = models.CharField(max_length=100, blank=True)
    
    usuario_registro = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Inventario Porcino'
        verbose_name_plural = 'Inventarios Porcinos'

    def __str__(self):
        return f"Inventario {self.fecha}"


class TareaPorcinos(BaseModel):
    PRIORIDADES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_limite = models.DateTimeField(null=True, blank=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_porcinos')
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_porcinos_creadas')

    class Meta:
        ordering = ['-fecha_limite', '-created_at']
        verbose_name = 'Tarea Porcinos'
        verbose_name_plural = 'Tareas Porcinos'

    def __str__(self):
        return self.titulo


class AlertaPorcinos(BaseModel):
    TIPOS = [
        ('mortalidad_alta', 'Mortalidad Alta'),
        ('consumo_anormal', 'Consumo Anormal'),
        ('peso_bajo', 'Peso Bajo'),
        ('vacuna_pendiente', 'Vacuna Pendiente'),
    ]
    NIVELES = [
        ('critica', 'Crítica'),
        ('normal', 'Normal'),
    ]

    lote = models.ForeignKey(LotePorcino, on_delete=models.CASCADE, null=True, blank=True)
    usuario_destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_porcinos', null=True, blank=True)
    tipo_alerta = models.CharField(max_length=30, choices=TIPOS)
    nivel = models.CharField(max_length=10, choices=NIVELES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    corral_nombre = models.CharField(max_length=100, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_generacion']
        verbose_name = 'Alerta de Porcinos'
        verbose_name_plural = 'Alertas de Porcinos'

    def __str__(self):
        return f"{self.titulo} - {self.lote}"


class AnimalPorcino(BaseModel):
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('H', 'Hembra'),
    ]
    ETAPA_CHOICES = [
        ('lechon', 'Lechón'),
        ('destete', 'Destete'),
        ('engorde', 'Engorde'),
        ('reemplazo', 'Reemplazo'),
        ('reproductor', 'Reproductor'),
        ('descarte', 'Descarte'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    raza = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    etapa = models.CharField(max_length=20, choices=ETAPA_CHOICES, default='lechon')
    peso_actual = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    lote = models.ForeignKey(LotePorcino, on_delete=models.SET_NULL, null=True, blank=True, related_name='animales')
    foto = models.ImageField(upload_to='porcinos/animales/', null=True, blank=True)
    notas = models.TextField(blank=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Animal Porcino'
        verbose_name_plural = 'Animales Porcinos'

    def __str__(self):
        return f"{self.codigo} ({self.get_sexo_display()})"


class PlanVacunacion(BaseModel):
    lote = models.ForeignKey(LotePorcino, on_delete=models.CASCADE)
    fecha_programada = models.DateField('Fecha programada')
    nombre_vacuna = models.CharField('Nombre de la vacuna', max_length=100)
    fecha_aplicada = models.DateField('Fecha aplicada', null=True, blank=True)
    aplicada = models.BooleanField('Aplicada', default=False)
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Plan de Vacunación'
        verbose_name_plural = 'Planes de Vacunación'
        ordering = ['fecha_programada']

    def __str__(self):
        return f"{self.nombre_vacuna} - {self.lote}"


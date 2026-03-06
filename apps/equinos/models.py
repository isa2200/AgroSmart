from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Equino(BaseModel):
    SEXO_CHOICES = [('M', 'Macho'), ('H', 'Hembra')]
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vendido', 'Vendido'),
        ('fallecido', 'Fallecido'),
    ]

    nombre = models.CharField('Nombre', max_length=100)
    raza = models.CharField('Raza', max_length=100, blank=True)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', null=True, blank=True)
    sexo = models.CharField('Sexo', max_length=1, choices=SEXO_CHOICES)
    color = models.CharField('Color/Pelaje', max_length=50, blank=True)
    microchip = models.CharField('Microchip', max_length=50, blank=True, unique=True)
    padre = models.CharField('Padre', max_length=100, blank=True)
    madre = models.CharField('Madre', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='activo')
    foto = models.ImageField('Foto', upload_to='equinos/', null=True, blank=True)
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Equino'
        verbose_name_plural = 'Equinos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class RegistroDiario(BaseModel):
    equino = models.ForeignKey(Equino, on_delete=models.CASCADE, related_name='registros_diarios', null=True, blank=True)
    fecha = models.DateField('Fecha', default=timezone.now)
    actividad = models.CharField('Título/Actividad', max_length=200)
    tiempo_minutos = models.PositiveIntegerField('Tiempo (minutos)', default=0, null=True, blank=True)
    observaciones = models.TextField('Contexto del día', blank=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Responsable')

    class Meta:
        verbose_name = 'Bitácora Diaria'
        verbose_name_plural = 'Bitácoras Diarias'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha} - {self.actividad}"

class TratamientoSalud(BaseModel):
    TIPO_CHOICES = [
        ('vacuna', 'Vacunación'),
        ('vermifugo', 'Vermífugo'),
        ('herraje', 'Herraje/Cascos'),
        ('odontologia', 'Odontología'),
        ('veterinario', 'Consulta Veterinaria'),
        ('otro', 'Otro'),
    ]

    equino = models.ForeignKey(Equino, on_delete=models.CASCADE, related_name='tratamientos')
    fecha = models.DateField('Fecha', default=timezone.now)
    tipo = models.CharField('Tipo de tratamiento', max_length=20, choices=TIPO_CHOICES)
    producto = models.CharField('Producto/Medicamento', max_length=100, blank=True)
    dosis = models.CharField('Dosis', max_length=100, blank=True)
    veterinario = models.CharField('Veterinario/Responsable', max_length=100, blank=True)
    proxima_fecha = models.DateField('Próxima aplicación', null=True, blank=True)
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Tratamiento y Salud'
        verbose_name_plural = 'Tratamientos y Salud'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.equino} - {self.get_tipo_display()} - {self.fecha}"


class PlanVacunacion(BaseModel):
    equino = models.ForeignKey(Equino, on_delete=models.CASCADE)
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
        return f"{self.nombre_vacuna} - {self.equino}"

class Alimentacion(BaseModel):
    equino = models.ForeignKey(Equino, on_delete=models.CASCADE, related_name='alimentacion')
    fecha_inicio = models.DateField('Fecha de inicio', default=timezone.now)
    tipo_alimento = models.CharField('Tipo de alimento', max_length=100) # Concentrado, Heno, etc.
    cantidad_kg = models.DecimalField('Cantidad (kg/día)', max_digits=5, decimal_places=2)
    frecuencia = models.CharField('Frecuencia', max_length=100, default='Diario')
    observaciones = models.TextField('Observaciones', blank=True)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Alimentación'
        verbose_name_plural = 'Alimentación'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.equino} - {self.tipo_alimento}"

class Novedad(BaseModel):
    TIPO_CHOICES = [
        ('medica', 'Médica'),
        ('comportamiento', 'Comportamiento'),
        ('movimiento', 'Movimiento/Traslado'),
        ('reproductiva', 'Reproductiva'),
        ('otra', 'Otra'),
    ]

    equino = models.ForeignKey(Equino, on_delete=models.CASCADE, related_name='novedades')
    fecha = models.DateField('Fecha', default=timezone.now)
    tipo = models.CharField('Tipo de novedad', max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField('Descripción')
    reportado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Novedad'
        verbose_name_plural = 'Novedades'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.equino} - {self.get_tipo_display()} - {self.fecha}"

class Observacion(BaseModel):
    equino = models.ForeignKey(Equino, on_delete=models.CASCADE, related_name='observaciones_set')
    fecha = models.DateField('Fecha', default=timezone.now)
    descripcion = models.TextField('Descripción')
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Observación'
        verbose_name_plural = 'Observaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"Observación - {self.equino} - {self.fecha}"

class Tarea(BaseModel):
    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
    ]

    titulo = models.CharField('Título', max_length=200)
    descripcion = models.TextField('Descripción', blank=True, null=True)
    prioridad = models.CharField('Prioridad', max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_limite = models.DateTimeField('Fecha Límite', blank=True, null=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_equinos', verbose_name='Responsable')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

    def __str__(self):
        return self.titulo

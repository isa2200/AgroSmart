from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from apps.core.models import BaseModel
import json

class TareaCunicultura(BaseModel):
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
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_cunicultura')
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_cunicultura_creadas')

    class Meta:
        ordering = ['-fecha_limite', '-created_at']
        verbose_name = 'Tarea Cunicultura'
        verbose_name_plural = 'Tareas Cunicultura'

    def __str__(self):
        return self.titulo

class InventarioConejos(models.Model):
    fecha = models.DateField(default=timezone.now)
    detalle = models.CharField(max_length=200, help_text="Clasificación o detalle (ej. Parto Jaula #38)")
    jaula = models.CharField(max_length=50, blank=True, null=True)
    identificacion = models.CharField(max_length=50, blank=True, null=True)
    madre_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Madre #")
    
    # Novedades
    gazapos_vivos = models.IntegerField(default=0)
    gazapos_muertos = models.IntegerField(default=0)
    compra = models.IntegerField(default=0)
    venta = models.IntegerField(default=0)
    muerte = models.IntegerField(default=0)
    
    # Inventario
    macho_levante_ceba = models.IntegerField(default=0)
    hembra_levante_ceba = models.IntegerField(default=0)
    reproductores = models.IntegerField(default=0)
    hembra_reemplazo = models.IntegerField(default=0)
    hembra_no_lactando = models.IntegerField(default=0)
    hembra_lactando = models.IntegerField(default=0)
    gazapos = models.IntegerField(default=0)
    total = models.IntegerField(default=0, editable=False)
    firma_responsable = models.ImageField(upload_to='firmas/cunicultura/inventario/', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total = (self.macho_levante_ceba + self.hembra_levante_ceba + 
                      self.reproductores + self.hembra_reemplazo + 
                      self.hembra_no_lactando + self.hembra_lactando + self.gazapos)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Inventario Permanente Conejos"
        verbose_name_plural = "Inventarios Permanentes Conejos"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha} - {self.detalle}"


class LibroDiarioConejos(models.Model):
    fecha = models.DateField(default=timezone.now)
    
    # Partos
    parto_jaula = models.CharField(max_length=50, blank=True, null=True)
    parto_vivos = models.IntegerField(default=0)
    parto_muertos = models.IntegerField(default=0)
    
    # Palpación
    palpacion_jaula = models.CharField(max_length=50, blank=True, null=True)
    palpacion_estado = models.CharField(max_length=50, blank=True, null=True)
    
    # Montas
    monta_jaula = models.CharField(max_length=50, blank=True, null=True)
    monta_macho = models.CharField(max_length=50, blank=True, null=True)
    
    # Destetes
    destete_jaula = models.CharField(max_length=50, blank=True, null=True)
    destete_cantidad_hembras = models.IntegerField(default=0)
    destete_cantidad_machos = models.IntegerField(default=0)
    destete_peso_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Muertes
    muerte_jaula = models.CharField(max_length=50, blank=True, null=True)
    muerte_gazapos = models.IntegerField(default=0)
    muerte_levante_ceba = models.IntegerField(default=0)
    muerte_reproductores = models.IntegerField(default=0)
    
    # Manejo Gazapera
    gazapera_poner_jaula = models.CharField(max_length=50, blank=True, null=True, verbose_name="Poner Jaula")
    gazapera_quitar_jaula = models.CharField(max_length=50, blank=True, null=True, verbose_name="Quitar Jaula")

    # Ventas
    venta_jaula = models.CharField(max_length=50, blank=True, null=True)
    venta_levante_ceba = models.IntegerField(default=0)
    venta_pie_cria = models.IntegerField(default=0)
    
    tratamientos = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # Alimentación (Resumen diario)
    alimentacion_am = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, verbose_name="Alimentación AM")
    alimentacion_pm = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, verbose_name="Alimentación PM")
    alimentacion_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    
    # Deprecated fields (kept for historical data)
    alimentacion_levante_ceba = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    alimentacion_reproduccion = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.alimentacion_total = (self.alimentacion_am or 0) + (self.alimentacion_pm or 0)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Libro Diario Conejos"
        verbose_name_plural = "Libros Diarios Conejos"
        ordering = ['-fecha']

    def __str__(self):
        return f"Libro Diario - {self.fecha}"


class RegistroAlimentoConejos(models.Model):
    fecha = models.DateField(default=timezone.now)
    unidad = models.CharField(max_length=50, default="Kg")
    entrada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salida = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Registro Alimento Conejos"
        verbose_name_plural = "Registros Alimento Conejos"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha} - Saldo: {self.saldo}"


class BitacoraActividadesConejos(models.Model):
    fecha = models.DateField(default=timezone.now)
    actividad = models.TextField()
    responsable = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = "Bitácora Actividades Conejos"
        verbose_name_plural = "Bitácoras Actividades Conejos"
        ordering = ['-fecha']
        
    def __str__(self):
        return f"{self.fecha} - {self.actividad[:30]}"


class ControlDestetes(models.Model):
    camada_numero = models.CharField(max_length=50)
    numero_animales = models.IntegerField()
    hembras_cantidad = models.IntegerField(default=0, verbose_name="H")
    hembras_peso_promedio = models.DecimalField(max_digits=6, decimal_places=3, default=0, verbose_name="Peso X H")
    machos_cantidad = models.IntegerField(default=0, verbose_name="M")
    machos_peso_promedio = models.DecimalField(max_digits=6, decimal_places=3, default=0, verbose_name="Peso X M")
    madre_numero = models.CharField(max_length=50)
    padre_numero = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    fecha_destete = models.DateField()
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Control Destete"
        verbose_name_plural = "Controles Destetes"
        ordering = ['-fecha_destete']

    def __str__(self):
        return f"Camada {self.camada_numero} - {self.fecha_destete}"

class PrecioConejo(models.Model):
    descripcion = models.CharField(max_length=100, default="Conejo en pie")
    edad_dias = models.CharField(max_length=50, help_text="Rango de edad (ej. 35 a 42)")
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    orden = models.IntegerField(default=0, help_text="Orden de visualización")

    class Meta:
        verbose_name = "Precio Conejo"
        verbose_name_plural = "Precios Conejos"
        ordering = ['orden', 'id']

    def __str__(self):
        return f"{self.descripcion} ({self.edad_dias})"


class PlanVacunacion(BaseModel):
    fecha_programada = models.DateField('Fecha programada')
    nombre_vacuna = models.CharField('Nombre de la vacuna', max_length=100)
    detalle = models.CharField('Detalle (Jaula/Lote)', max_length=100)
    fecha_aplicada = models.DateField('Fecha aplicada', null=True, blank=True)
    aplicada = models.BooleanField('Aplicada', default=False)
    observaciones = models.TextField('Observaciones', blank=True)
    
    class Meta:
        verbose_name = 'Plan de Vacunación'
        verbose_name_plural = 'Planes de Vacunación'
        ordering = ['fecha_programada']

    def __str__(self):
        return f"{self.nombre_vacuna} - {self.detalle}"

class HistorialInventarioConejos(models.Model):
    ACCIONES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('ELIMINAR', 'Eliminar'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    fecha_accion = models.DateTimeField(auto_now_add=True)
    justificacion = models.TextField(blank=True, null=True)
    
    # Datos del registro afectado (Snapshot)
    registro_id = models.IntegerField(null=True, blank=True, help_text="ID del registro original")
    fecha_registro = models.DateField(null=True, blank=True)
    detalle_registro = models.CharField(max_length=200, null=True, blank=True)
    
    # JSON con los datos anteriores (para ediciones/eliminaciones)
    datos_anteriores = models.TextField(null=True, blank=True, help_text="JSON con los datos del registro")
    
    class Meta:
        verbose_name = "Historial Inventario Conejos"
        verbose_name_plural = "Historiales Inventario Conejos"
        ordering = ['-fecha_accion']

    def __str__(self):
        return f"{self.get_accion_display()} - {self.fecha_registro} ({self.detalle_registro})"

    def get_datos_dict(self):
        if self.datos_anteriores:
            try:
                return json.loads(self.datos_anteriores)
            except:
                return {}
        return {}

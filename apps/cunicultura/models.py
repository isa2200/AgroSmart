from django.db import models
from django.utils import timezone

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
    alimentacion_levante_ceba = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    alimentacion_reproduccion = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    alimentacion_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)

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
    sexo = models.CharField(max_length=10, choices=[('H', 'Hembra'), ('M', 'Macho'), ('Mixto', 'Mixto')])
    peso_promedio = models.DecimalField(max_digits=6, decimal_places=3, help_text="Peso promedio en Kg/g")
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















































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































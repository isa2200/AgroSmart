"""
Modelos para el módulo avícola de AgroSmart.
Sistema integral de gestión de gallinas ponedoras.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from apps.core.models import BaseModel


class LoteAves(BaseModel):
    """Lotes de aves ponedoras."""
    ESTADOS = [
        ('levante', 'Pollas de Levante'),
        ('postura', 'En Postura'),
        ('finalizado', 'Finalizado'),
    ]
    
    LINEAS_GENETICAS = [
        ('hy_line_brown', 'Hy-Line Brown'),
        ('hy_line_white', 'Hy-Line White'),
        ('lohmann_brown', 'Lohmann Brown'),
        ('lohmann_white', 'Lohmann White'),
        ('isa_brown', 'ISA Brown'),
        ('isa_white', 'ISA White'),
        ('bovans_brown', 'Bovans Brown'),
        ('bovans_white', 'Bovans White'),
        ('dekalb_brown', 'Dekalb Brown'),
        ('dekalb_white', 'Dekalb White'),
        ('otra', 'Otra'),
    ]
    
    codigo = models.CharField('Código del lote', max_length=50, unique=True)
    galpon = models.CharField('Galpón', max_length=100)
    linea_genetica = models.CharField('Línea genética', max_length=50, choices=LINEAS_GENETICAS)
    procedencia = models.CharField('Procedencia', max_length=200)
    numero_aves_inicial = models.PositiveIntegerField('Número inicial de aves')
    numero_aves_actual = models.PositiveIntegerField('Número actual de aves')
    fecha_llegada = models.DateField('Fecha de llegada')
    fecha_inicio_postura = models.DateField('Fecha inicio postura', null=True, blank=True)
    peso_total_llegada = models.DecimalField('Peso total llegada (kg)', max_digits=10, decimal_places=2)
    peso_promedio_llegada = models.DecimalField('Peso promedio llegada (g)', max_digits=8, decimal_places=2)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='levante')
    observaciones = models.TextField('Observaciones', blank=True)
    
    class Meta:
        verbose_name = 'Lote de Aves'
        verbose_name_plural = 'Lotes de Aves'
        ordering = ['-fecha_llegada']
    
    def __str__(self):
        return f"{self.codigo} - {self.galpon}"
    
    @property
    def edad_dias(self):
        """Calcula la edad del lote en días."""
        return (timezone.now().date() - self.fecha_llegada).days
    
    @property
    def mortalidad_total(self):
        """Calcula la mortalidad total del lote."""
        return self.numero_aves_inicial - self.numero_aves_actual
    
    @property
    def porcentaje_mortalidad(self):
        """Calcula el porcentaje de mortalidad del lote."""
        if self.numero_aves_inicial > 0:
            return round((self.mortalidad_total / self.numero_aves_inicial) * 100, 2)
        return 0
    
    def get_linea_genetica_display_name(self):
        """Retorna el nombre completo de la línea genética."""
        return dict(self.LINEAS_GENETICAS).get(self.linea_genetica, self.linea_genetica)


class BitacoraDiaria(BaseModel):
    """Bitácora diaria unificada de producción."""
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE, verbose_name='Lote')
    fecha = models.DateField('Fecha')
    
    # Información del lote
    semana_vida = models.PositiveIntegerField('Semana de vida', null=True, blank=True)
    
    # Producción por categoría
    produccion_aaa = models.PositiveIntegerField('Producción AAA', default=0)
    produccion_aa = models.PositiveIntegerField('Producción AA', default=0)
    produccion_a = models.PositiveIntegerField('Producción A', default=0)
    produccion_b = models.PositiveIntegerField('Producción B', default=0)
    produccion_c = models.PositiveIntegerField('Producción C', default=0)
    
    # Mortalidad y consumo
    mortalidad = models.PositiveIntegerField('Mortalidad', default=0)
    causa_mortalidad = models.CharField('Causa de mortalidad', max_length=200, blank=True)
    consumo_concentrado = models.DecimalField('Consumo concentrado (kg)', max_digits=10, decimal_places=2, default=0)
    
    observaciones = models.TextField('Observaciones', blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario que registra')
    
    class Meta:
        verbose_name = 'Bitácora Diaria'
        verbose_name_plural = 'Bitácoras Diarias'
        unique_together = ['lote', 'fecha']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.lote.codigo} - {self.fecha}"
    
    @property
    def produccion_total(self):
        """Calcula la producción total del día."""
        return (self.produccion_aaa + self.produccion_aa + self.produccion_a + 
                self.produccion_b + self.produccion_c)
    
    @property
    def porcentaje_postura(self):
        """Calcula el porcentaje de postura."""
        if self.lote.numero_aves_actual > 0:
            return (self.produccion_total / self.lote.numero_aves_actual) * 100
        return 0
    
    def save(self, *args, **kwargs):
        # Calcular semana de vida automáticamente si no se proporciona
        if not self.semana_vida and self.lote.fecha_llegada:
            dias_vida = (self.fecha - self.lote.fecha_llegada).days
            self.semana_vida = (dias_vida // 7) + 1
            
        # Actualizar número de aves actual del lote si hay mortalidad
        if self.mortalidad > 0:
            self.lote.numero_aves_actual = max(0, self.lote.numero_aves_actual - self.mortalidad)
            self.lote.save()
        super().save(*args, **kwargs)


class TipoConcentrado(BaseModel):
    """Tipos de concentrado para aves."""
    nombre = models.CharField('Nombre', max_length=100)
    descripcion = models.TextField('Descripción', blank=True)
    proteina_porcentaje = models.DecimalField('% Proteína', max_digits=5, decimal_places=2)
    precio_por_kg = models.DecimalField('Precio por kg', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Tipo de Concentrado'
        verbose_name_plural = 'Tipos de Concentrado'
    
    def __str__(self):
        return self.nombre


class ControlConcentrado(BaseModel):
    """Control de entrada y salida de concentrado."""
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    
    tipo_concentrado = models.ForeignKey(TipoConcentrado, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField('Tipo de movimiento', max_length=10, choices=TIPOS_MOVIMIENTO)
    cantidad_kg = models.DecimalField('Cantidad (kg)', max_digits=10, decimal_places=2)
    fecha = models.DateField('Fecha')
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Lote destino')
    galpon_destino = models.CharField('Galpón destino', max_length=100, blank=True)
    proveedor = models.CharField('Proveedor', max_length=200, blank=True)
    numero_factura = models.CharField('Número de factura', max_length=100, blank=True)
    observaciones = models.TextField('Observaciones', blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Control de Concentrado'
        verbose_name_plural = 'Control de Concentrados'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.tipo_concentrado.nombre} - {self.fecha} - {self.tipo_movimiento}"


class TipoVacuna(BaseModel):
    """Tipos de vacunas para aves."""
    nombre = models.CharField('Nombre de la vacuna', max_length=100)
    laboratorio = models.CharField('Laboratorio', max_length=100)
    enfermedad_previene = models.CharField('Enfermedad que previene', max_length=200)
    via_aplicacion = models.CharField('Vía de aplicación', max_length=100)
    dosis_por_ave = models.DecimalField('Dosis por ave (ml)', max_digits=5, decimal_places=2)
    intervalo_dias = models.PositiveIntegerField('Intervalo entre dosis (días)', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Tipo de Vacuna'
        verbose_name_plural = 'Tipos de Vacunas'
    
    def __str__(self):
        return f"{self.nombre} - {self.laboratorio}"


class PlanVacunacion(BaseModel):
    """Plan de vacunación para lotes."""
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE)
    tipo_vacuna = models.ForeignKey(TipoVacuna, on_delete=models.CASCADE)
    fecha_programada = models.DateField('Fecha programada')
    fecha_aplicada = models.DateField('Fecha aplicada', null=True, blank=True)
    numero_aves_vacunadas = models.PositiveIntegerField('Número de aves vacunadas', null=True, blank=True)
    lote_vacuna = models.CharField('Lote de vacuna', max_length=100, blank=True)
    veterinario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Veterinario')
    observaciones = models.TextField('Observaciones', blank=True)
    aplicada = models.BooleanField('Aplicada', default=False)
    
    class Meta:
        verbose_name = 'Plan de Vacunación'
        verbose_name_plural = 'Planes de Vacunación'
        ordering = ['fecha_programada']
    
    def __str__(self):
        return f"{self.lote.codigo} - {self.tipo_vacuna.nombre} - {self.fecha_programada}"
    
    @property
    def dias_para_aplicacion(self):
        """Días restantes para la aplicación."""
        if not self.aplicada:
            return (self.fecha_programada - timezone.now().date()).days
        return 0


class MovimientoHuevos(BaseModel):
    """Movimientos de huevos (despachos, ventas, autoconsumo) - Encabezado."""
    TIPOS_MOVIMIENTO = [
        ('venta', 'Venta'),
        ('autoconsumo', 'Autoconsumo'),
        ('baja', 'Baja'),
        ('devolucion', 'Devolución'),
    ]
    
    CATEGORIAS_HUEVO = [
        ('AAA', 'AAA'),
        ('AA', 'AA'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    
    fecha = models.DateField('Fecha')
    tipo_movimiento = models.CharField('Tipo de movimiento', max_length=15, choices=TIPOS_MOVIMIENTO)
    cliente = models.CharField('Cliente/Destino', max_length=200, blank=True)
    conductor = models.CharField('Conductor', max_length=200, blank=True)
    numero_comprobante = models.CharField('Número de comprobante', max_length=100, blank=True)
    observaciones = models.TextField('Observaciones', blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Movimiento de Huevos'
        verbose_name_plural = 'Movimientos de Huevos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.fecha} - {self.cliente}"
    
    @property
    def cantidad_total(self):
        """Calcula la cantidad total de huevos en el movimiento."""
        return sum(detalle.cantidad for detalle in self.detalles.all())
    
    @property
    def valor_total(self):
        """Calcula el valor total del movimiento."""
        return sum(detalle.subtotal for detalle in self.detalles.all())


class DetalleMovimientoHuevos(BaseModel):
    """Detalle de movimiento de huevos por categoría."""
    movimiento = models.ForeignKey(
        MovimientoHuevos, 
        on_delete=models.CASCADE, 
        related_name='detalles',
        verbose_name='Movimiento'
    )
    categoria_huevo = models.CharField(
        'Categoría', 
        max_length=3, 
        choices=MovimientoHuevos.CATEGORIAS_HUEVO
    )
    cantidad = models.PositiveIntegerField('Cantidad')
    precio_unitario = models.DecimalField(
        'Precio unitario', 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name = 'Detalle de Movimiento de Huevos'
        verbose_name_plural = 'Detalles de Movimientos de Huevos'
        unique_together = ['movimiento', 'categoria_huevo']
    
    def __str__(self):
        return f"{self.movimiento} - {self.categoria_huevo} - {self.cantidad}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal del detalle."""
        if self.precio_unitario:
            return self.cantidad * self.precio_unitario
        return 0
    
    def clean(self):
        """Validaciones del modelo."""
        from django.core.exceptions import ValidationError
        
        # Validar que los campos requeridos tengan valores válidos
        if not self.categoria_huevo:
            raise ValidationError({'categoria_huevo': 'La categoría de huevo es requerida.'})
        
        if self.cantidad is None or self.cantidad <= 0:
            raise ValidationError({'cantidad': 'La cantidad debe ser mayor a 0.'})
        
        # Validar precio unitario si está presente
        if self.precio_unitario is not None and self.precio_unitario < 0:
            raise ValidationError({'precio_unitario': 'El precio unitario no puede ser negativo.'})
        
        # Validar stock solo para movimientos que requieren validación de stock
        # Solo validar si tenemos un movimiento válido, cantidad válida y es un movimiento de salida
        if (hasattr(self, 'movimiento') and self.movimiento and 
            self.movimiento.tipo_movimiento in ['venta', 'autoconsumo', 'baja'] and
            self.cantidad is not None and self.cantidad > 0 and
            self.categoria_huevo):
            
            try:
                inventario = InventarioHuevos.objects.get(categoria=self.categoria_huevo)
                
                # Si estamos editando un detalle existente, considerar la cantidad anterior
                cantidad_a_validar = self.cantidad
                if self.pk:  # Si es una edición
                    try:
                        detalle_anterior = DetalleMovimientoHuevos.objects.get(pk=self.pk)
                        # Restaurar la cantidad anterior al stock para validar correctamente
                        stock_disponible = inventario.cantidad_actual + detalle_anterior.cantidad
                    except DetalleMovimientoHuevos.DoesNotExist:
                        stock_disponible = inventario.cantidad_actual
                else:
                    stock_disponible = inventario.cantidad_actual
                
                if cantidad_a_validar > stock_disponible:
                    raise ValidationError({
                        'cantidad': f'No hay suficiente stock de huevos {self.categoria_huevo}. '
                                   f'Stock disponible: {stock_disponible}'
                    })
                    
            except InventarioHuevos.DoesNotExist:
                raise ValidationError({
                    'categoria_huevo': f'No existe inventario para la categoría {self.categoria_huevo}. '
                                      f'Debe crear el inventario primero.'
                })


class InventarioHuevos(BaseModel):
    """Inventario actual de huevos por categoría."""
    categoria = models.CharField('Categoría', max_length=3, choices=MovimientoHuevos.CATEGORIAS_HUEVO, unique=True)
    cantidad_actual = models.PositiveIntegerField('Cantidad actual', default=0)
    cantidad_minima = models.PositiveIntegerField('Cantidad mínima', default=100)
    # Nuevos campos para stock automático
    stock_automatico = models.BooleanField('Stock automático', default=True, help_text='Si está activado, el stock mínimo se calcula automáticamente basado en la cantidad de gallinas')
    factor_calculo = models.DecimalField('Factor de cálculo', max_digits=5, decimal_places=2, default=0.75, help_text='Factor multiplicador para calcular stock mínimo (ej: 0.75 = 75% de producción esperada)')
    dias_stock = models.PositiveIntegerField('Días de stock', default=3, help_text='Número de días de stock mínimo a mantener')
    fecha_ultima_actualizacion = models.DateTimeField('Última actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Inventario de Huevos'
        verbose_name_plural = 'Inventarios de Huevos'
    
    def __str__(self):
        return f"Categoría {self.categoria}: {self.cantidad_actual} unidades"
    
    @property
    def necesita_reposicion(self):
        """Indica si el inventario está por debajo del mínimo."""
        return self.cantidad_actual <= self.cantidad_minima_calculada
    
    @property
    def cantidad_minima_calculada(self):
        """Calcula la cantidad mínima basada en la configuración."""
        if self.stock_automatico:
            return self.calcular_stock_minimo_automatico()
        return self.cantidad_minima
    
    def calcular_stock_minimo_automatico(self):
        """Calcula el stock mínimo automáticamente basado en la cantidad de gallinas."""
        from django.db.models import Sum
        
        # Obtener total de gallinas en postura (activas)
        total_gallinas = LoteAves.objects.filter(
            is_active=True,
            estado='postura'
        ).aggregate(total=Sum('numero_aves_actual'))['total'] or 0
        
        if total_gallinas == 0:
            return self.cantidad_minima  # Fallback al valor manual
        
        # Calcular producción esperada por día para esta categoría
        # Factores de distribución por categoría (basado en estándares avícolas)
        factores_categoria = {
            'AAA': 0.40,  # 40% de la producción
            'AA': 0.35,   # 35% de la producción
            'A': 0.15,    # 15% de la producción
            'B': 0.08,    # 8% de la producción
            'C': 0.02,    # 2% de la producción
        }
        
        factor_categoria = factores_categoria.get(self.categoria, 0.20)
        
        # Cálculo: Total gallinas × Factor de producción × Factor de categoría × Días de stock
        produccion_esperada_dia = total_gallinas * float(self.factor_calculo) * factor_categoria
        stock_minimo = int(produccion_esperada_dia * self.dias_stock)
        
        # Asegurar un mínimo absoluto
        return max(stock_minimo, 50)
    
    def actualizar_stock_minimo(self):
        """Actualiza el stock mínimo si está en modo automático."""
        if self.stock_automatico:
            nuevo_minimo = self.calcular_stock_minimo_automatico()
            if nuevo_minimo != self.cantidad_minima:
                self.cantidad_minima = nuevo_minimo
                self.save(update_fields=['cantidad_minima', 'fecha_ultima_actualizacion'])
                return True
        return False
    
    def save(self, *args, **kwargs):
        """Override save para actualizar stock automático."""
        if self.stock_automatico:
            self.cantidad_minima = self.calcular_stock_minimo_automatico()
        super().save(*args, **kwargs)


class AlertaSistema(BaseModel):
    """Sistema de alertas para el módulo avícola."""
    TIPOS_ALERTA = [
        ('stock_bajo', 'Stock Bajo'),
        ('mortalidad_alta', 'Mortalidad Alta'),
        ('vacuna_pendiente', 'Vacuna Pendiente'),
        ('produccion_baja', 'Producción Baja'),
    ]
    
    NIVELES = [
        ('critica', 'Crítica'),
        ('normal', 'Normal'),
    ]
    
    tipo_alerta = models.CharField('Tipo de alerta', max_length=30, choices=TIPOS_ALERTA)
    nivel = models.CharField('Nivel', max_length=10, choices=NIVELES)
    titulo = models.CharField('Título', max_length=200)
    mensaje = models.TextField('Mensaje')
    lote = models.ForeignKey(LoteAves, on_delete=models.CASCADE, null=True, blank=True)
    galpon_nombre = models.CharField('Galpón', max_length=100, blank=True)
    fecha_generacion = models.DateTimeField('Fecha de generación', auto_now_add=True)
    leida = models.BooleanField('Leída', default=False)
    usuario_destinatario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='alertas_aves'
    )
    
    class Meta:
        verbose_name = 'Alerta del Sistema'
        verbose_name_plural = 'Alertas del Sistema'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha_generacion.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def es_critica(self):
        """Determina si la alerta es crítica basándose en el tipo y contenido."""
        return self.nivel == 'critica'
    
    @property
    def icono(self):
        """Retorna el icono apropiado según el tipo de alerta."""
        iconos = {
            'mortalidad_alta': 'fas fa-skull-crossbones',
            'produccion_baja': 'fas fa-egg',
            'vacuna_pendiente': 'fas fa-syringe',
            'stock_bajo': 'fas fa-boxes',
        }
        return iconos.get(self.tipo_alerta, 'fas fa-bell')
    
    @property
    def color_clase(self):
        """Retorna la clase CSS apropiada según el nivel."""
        return 'danger' if self.nivel == 'critica' else 'warning'


class RegistroModificacion(BaseModel):
    """Registro de modificaciones para auditoría."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    modelo = models.CharField('Modelo', max_length=100)
    objeto_id = models.PositiveIntegerField('ID del objeto')
    accion = models.CharField('Acción', max_length=20)  # CREATE, UPDATE, DELETE
    campos_modificados = models.JSONField('Campos modificados', default=dict)
    valores_anteriores = models.JSONField('Valores anteriores', default=dict)
    valores_nuevos = models.JSONField('Valores nuevos', default=dict)
    justificacion = models.TextField('Justificación', blank=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro de Modificación'
        verbose_name_plural = 'Registros de Modificaciones'
        ordering = ['-fecha_modificacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.modelo} - {self.fecha_modificacion}"
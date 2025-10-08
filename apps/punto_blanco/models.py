from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel
from apps.aves.models import InventarioHuevos


class Pedido(BaseModel):
    """Modelo para gestionar pedidos del punto blanco"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo para Entrega'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_ENTREGA_CHOICES = [
        ('recoger', 'Recoger en Punto'),
        ('domicilio', 'Entrega a Domicilio'),
    ]
    
    numero_pedido = models.CharField('Número de Pedido', max_length=20, unique=True)
    usuario_punto_blanco = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Usuario Punto Blanco',
        related_name='pedidos_punto_blanco'
    )
    cliente_nombre = models.CharField('Nombre del Cliente', max_length=100)
    cliente_telefono = models.CharField('Teléfono del Cliente', max_length=15)
    cliente_email = models.EmailField('Email del Cliente', blank=True)
    cliente_direccion = models.TextField('Dirección del Cliente', blank=True)
    
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    tipo_entrega = models.CharField('Tipo de Entrega', max_length=20, choices=TIPO_ENTREGA_CHOICES, default='recoger')
    
    fecha_pedido = models.DateTimeField('Fecha del Pedido', auto_now_add=True)
    fecha_entrega_estimada = models.DateTimeField('Fecha de Entrega Estimada', null=True, blank=True)
    fecha_entrega_real = models.DateTimeField('Fecha de Entrega Real', null=True, blank=True)
    
    observaciones = models.TextField('Observaciones', blank=True)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido {self.numero_pedido} - {self.cliente_nombre}"
    
    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Generar número de pedido automático
            import datetime
            fecha = datetime.datetime.now()
            ultimo_pedido = Pedido.objects.filter(
                numero_pedido__startswith=f"PB{fecha.strftime('%Y%m%d')}"
            ).order_by('-numero_pedido').first()
            
            if ultimo_pedido:
                ultimo_numero = int(ultimo_pedido.numero_pedido[-3:])
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
                
            self.numero_pedido = f"PB{fecha.strftime('%Y%m%d')}{nuevo_numero:03d}"
        
        super().save(*args, **kwargs)
    
    def calcular_total(self):
        """Calcula el total del pedido basado en los detalles"""
        total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.total = total
        self.save(update_fields=['total'])
        return total
    
    def puede_ser_cancelado(self):
        """Verifica si el pedido puede ser cancelado"""
        return self.estado in ['pendiente', 'confirmado']
    
    def puede_ser_confirmado(self):
        """Verifica si el pedido puede ser confirmado"""
        return self.estado == 'pendiente'


class DetallePedido(BaseModel):
    """Detalle de productos en un pedido"""
    
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='detalles',
        verbose_name='Pedido'
    )
    inventario_huevos = models.ForeignKey(
        InventarioHuevos,
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    cantidad = models.PositiveIntegerField('Cantidad')
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=8, decimal_places=2)
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'
        unique_together = ['pedido', 'inventario_huevos']
    
    def __str__(self):
        return f"{self.pedido.numero_pedido} - {self.inventario_huevos.categoria} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        
        # Actualizar total del pedido
        self.pedido.calcular_total()
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validar que hay suficiente stock
        if self.cantidad > self.inventario_huevos.cantidad_actual:
            raise ValidationError(
                f'No hay suficiente stock. Disponible: {self.inventario_huevos.cantidad_actual}'
            )


class ConfiguracionPuntoBlanco(BaseModel):
    """Configuración específica para el punto blanco"""
    
    nombre_punto = models.CharField('Nombre del Punto', max_length=100, default='Punto Blanco')
    direccion = models.TextField('Dirección')
    telefono = models.CharField('Teléfono', max_length=15)
    email = models.EmailField('Email', blank=True)
    
    # Configuración de precios
    margen_ganancia_default = models.DecimalField(
        'Margen de Ganancia Default (%)', 
        max_digits=5, 
        decimal_places=2, 
        default=20.00
    )
    
    # Configuración de horarios
    hora_apertura = models.TimeField('Hora de Apertura', default='08:00')
    hora_cierre = models.TimeField('Hora de Cierre', default='18:00')
    
    # Configuración de entrega
    costo_domicilio = models.DecimalField(
        'Costo de Domicilio', 
        max_digits=8, 
        decimal_places=2, 
        default=0
    )
    radio_entrega_km = models.PositiveIntegerField('Radio de Entrega (km)', default=10)
    
    activo = models.BooleanField('Activo', default=True)
    
    class Meta:
        verbose_name = 'Configuración Punto Blanco'
        verbose_name_plural = 'Configuraciones Punto Blanco'
    
    def __str__(self):
        return self.nombre_punto
    
    @classmethod
    def get_configuracion(cls):
        """Obtiene la configuración activa"""
        config = cls.objects.filter(activo=True).first()
        if not config:
            config = cls.objects.create(
                nombre_punto='Punto Blanco',
                direccion='Dirección no configurada',
                telefono='000-000-0000'
            )
        return config
from django.contrib import admin
from .models import Pedido, DetallePedido, ConfiguracionPuntoBlanco


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    readonly_fields = ('subtotal',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_pedido', 'cliente_nombre', 'estado', 
        'total', 'fecha_pedido', 'usuario_punto_blanco'
    ]
    list_filter = ['estado', 'tipo_entrega', 'fecha_pedido']
    search_fields = ['numero_pedido', 'cliente_nombre', 'cliente_telefono']
    readonly_fields = ['numero_pedido', 'total', 'fecha_pedido']
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario_punto_blanco', 'estado', 'total')
        }),
        ('Información del Cliente', {
            'fields': ('cliente_nombre', 'cliente_telefono', 'cliente_email', 'cliente_direccion')
        }),
        ('Entrega', {
            'fields': ('tipo_entrega', 'fecha_entrega_estimada', 'fecha_entrega_real')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'inventario_huevos', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['pedido__estado', 'inventario_huevos__categoria']


@admin.register(ConfiguracionPuntoBlanco)
class ConfiguracionPuntoBlancoAdmin(admin.ModelAdmin):
    list_display = ['nombre_punto', 'telefono', 'activo']
    fieldsets = (
        ('Información General', {
            'fields': ('nombre_punto', 'direccion', 'telefono', 'email', 'activo')
        }),
        ('Configuración de Precios', {
            'fields': ('margen_ganancia_default',)
        }),
        ('Horarios', {
            'fields': ('hora_apertura', 'hora_cierre')
        }),
        ('Entrega a Domicilio', {
            'fields': ('costo_domicilio', 'radio_entrega_km')
        }),
    )
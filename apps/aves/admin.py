"""
Configuración del admin para el módulo avícola.
"""

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    LoteAves, BitacoraDiaria, TipoConcentrado,
    ControlConcentrado, TipoVacuna, PlanVacunacion,
    MovimientoHuevos, DetalleMovimientoHuevos, InventarioHuevos, AlertaSistema,
    RegistroModificacion
)


class FiltroFechaPersonalizado(SimpleListFilter):
    """Filtro personalizado para fechas."""
    title = 'Período'
    parameter_name = 'periodo'

    def lookups(self, request, model_admin):
        return (
            ('hoy', 'Hoy'),
            ('semana', 'Esta semana'),
            ('mes', 'Este mes'),
            ('trimestre', 'Este trimestre'),
        )

    def queryset(self, request, queryset):
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        if self.value() == 'hoy':
            return queryset.filter(fecha=timezone.now().date())
        elif self.value() == 'semana':
            inicio_semana = timezone.now().date() - timedelta(days=7)
            return queryset.filter(fecha__gte=inicio_semana)
        elif self.value() == 'mes':
            inicio_mes = timezone.now().date().replace(day=1)
            return queryset.filter(fecha__gte=inicio_mes)
        elif self.value() == 'trimestre':
            inicio_trimestre = timezone.now().date() - timedelta(days=90)
            return queryset.filter(fecha__gte=inicio_trimestre)

@admin.register(LoteAves)
class LoteAvesAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'galpon', 'linea_genetica', 'numero_aves_inicial', 'numero_aves_actual', 'fecha_llegada', 'estado']
    list_filter = ['estado', 'linea_genetica', FiltroFechaPersonalizado]
    search_fields = ['codigo', 'galpon', 'procedencia']
    date_hierarchy = 'fecha_llegada'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'galpon', 'linea_genetica', 'procedencia')
        }),
        ('Datos de Llegada', {
            'fields': ('numero_aves_inicial', 'fecha_llegada', 'peso_total_llegada', 'peso_promedio_llegada')
        }),
        ('Estado Actual', {
            'fields': ('numero_aves_actual', 'estado', 'fecha_inicio_postura')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )
    
    readonly_fields = ['numero_aves_actual']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.numero_aves_actual = obj.numero_aves_inicial
        super().save_model(request, obj, form, change)

@admin.register(BitacoraDiaria)
class BitacoraDiariaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'produccion_total', 'mortalidad', 'consumo_concentrado']
    list_filter = ['fecha', 'lote']
    search_fields = ['lote__codigo', 'observaciones']
    ordering = ['-fecha']
    readonly_fields = ['created_at', 'updated_at', 'produccion_total', 'porcentaje_postura']
    date_hierarchy = 'fecha'

@admin.register(TipoConcentrado)
class TipoConcentradoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'proteina_porcentaje', 'precio_por_kg']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

@admin.register(ControlConcentrado)
class ControlConcentradoAdmin(admin.ModelAdmin):
    list_display = ['tipo_concentrado', 'tipo_movimiento', 'cantidad_kg', 'fecha', 'lote', 'galpon_destino']
    list_filter = ['tipo_movimiento', 'fecha', 'tipo_concentrado']
    search_fields = ['tipo_concentrado__nombre', 'lote__codigo', 'galpon_destino', 'proveedor']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('tipo_concentrado', 'tipo_movimiento', 'cantidad_kg', 'fecha')
        }),
        ('Destino', {
            'fields': ('lote', 'galpon_destino')
        }),
        ('Información Comercial', {
            'fields': ('proveedor', 'numero_factura'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )
    search_fields = ['proveedor', 'numero_factura', 'lote__codigo', 'galpon_destino']
    ordering = ['-fecha']

@admin.register(TipoVacuna)
class TipoVacunaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'laboratorio', 'enfermedad_previene', 'via_aplicacion']
    search_fields = ['nombre', 'laboratorio', 'enfermedad_previene']
    ordering = ['nombre']

@admin.register(PlanVacunacion)
class PlanVacunacionAdmin(admin.ModelAdmin):
    list_display = ['lote', 'tipo_vacuna', 'fecha_programada', 'fecha_aplicada', 'aplicada']
    list_filter = ['aplicada', 'fecha_programada', 'tipo_vacuna']
    search_fields = ['lote__codigo', 'tipo_vacuna__nombre']
    ordering = ['fecha_programada']

class DetalleMovimientoHuevosInline(admin.TabularInline):
    """Inline para detalles de movimiento de huevos."""
    model = DetalleMovimientoHuevos
    extra = 1
    fields = ['categoria_huevo', 'cantidad_docenas', 'precio_por_docena']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si el objeto ya existe
            return ['categoria_huevo']
        return []

@admin.register(MovimientoHuevos)
class MovimientoHuevosAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'tipo_movimiento', 'cantidad_total_docenas', 'valor_total', 'cliente']
    list_filter = ['tipo_movimiento', 'fecha']
    search_fields = ['cliente', 'conductor', 'observaciones', 'numero_comprobante']
    ordering = ['-fecha']
    inlines = [DetalleMovimientoHuevosInline]
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('fecha', 'tipo_movimiento')
        }),
        ('Información del Cliente/Transporte', {
            'fields': ('cliente', 'conductor', 'numero_comprobante')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )
    
    readonly_fields = ['cantidad_total_docenas', 'valor_total']
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Si el objeto ya existe
            readonly.extend(['fecha', 'tipo_movimiento'])
        return readonly

@admin.register(DetalleMovimientoHuevos)
class DetalleMovimientoHuevosAdmin(admin.ModelAdmin):
    list_display = ['movimiento', 'categoria_huevo', 'cantidad_docenas', 'precio_por_docena', 'subtotal']
    list_filter = ['categoria_huevo', 'movimiento__tipo_movimiento', 'movimiento__fecha']
    search_fields = ['movimiento__cliente', 'movimiento__numero_comprobante']
    ordering = ['-movimiento__fecha', 'categoria_huevo']
    
    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Subtotal'
    
    def has_add_permission(self, request):
        # No permitir agregar detalles directamente, solo a través del movimiento
        return False

@admin.register(InventarioHuevos)
class InventarioHuevosAdmin(admin.ModelAdmin):
    list_display = ['categoria', 'cantidad_actual', 'cantidad_minima', 'necesita_reposicion']
    list_filter = ['categoria']
    ordering = ['categoria']

@admin.register(AlertaSistema)
class AlertaSistemaAdmin(admin.ModelAdmin):
    list_display = ['tipo_alerta', 'titulo', 'nivel', 'fecha_generacion', 'leida']
    list_filter = ['tipo_alerta', 'nivel', 'leida', 'fecha_generacion']
    search_fields = ['titulo', 'mensaje']
    ordering = ['-fecha_generacion']

@admin.register(RegistroModificacion)
class RegistroModificacionAdmin(admin.ModelAdmin):
    list_display = ['fecha_modificacion', 'usuario', 'modelo', 'accion', 'objeto_id']
    list_filter = ['accion', 'modelo', 'fecha_modificacion']
    search_fields = ['usuario__username', 'justificacion']
    ordering = ['-fecha_modificacion']
    readonly_fields = ['fecha_modificacion']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.site_header = "AgroSmart - Administración Avícola"
admin.site.site_title = "AgroSmart Admin"
admin.site.index_title = "Panel de Administración del Módulo Avícola"
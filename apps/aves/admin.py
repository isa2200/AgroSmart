"""
Configuración del admin para el módulo avícola.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Avg, Count
from django.contrib.admin import SimpleListFilter
from .models import (
    Galpon, LoteAves, BitacoraDiaria, PollasLevante, ProduccionHuevos,
    MovimientoHuevos, ControlConcentrados, PlanVacunacion, VacunacionRealizada,
    ControlTemperaturaHumedad, DespachoHuevos, AlertasSistema, HistorialCambios
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


@admin.register(Galpon)
class GalponAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nombre', 'capacidad_maxima', 'tipo_ave', 'estado_badge', 'created_at']
    list_filter = ['tipo_ave', 'is_active', 'created_at']
    search_fields = ['numero', 'nombre', 'descripcion']
    ordering = ['numero']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero', 'nombre', 'descripcion')
        }),
        ('Especificaciones', {
            'fields': ('capacidad_maxima', 'tipo_ave', 'area_m2')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Activo')
        return format_html('<span style="color: red;">●</span> Inactivo')
    estado_badge.short_description = 'Estado'


@admin.register(LoteAves)
class LoteAvesAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'galpon', 'linea_genetica', 'cantidad_inicial', 'cantidad_actual', 'estado_badge', 'semanas_edad']
    list_filter = ['galpon', 'linea_genetica', 'estado', 'fecha_ingreso']
    search_fields = ['codigo', 'procedencia', 'galpon__nombre']
    ordering = ['-fecha_ingreso']
    readonly_fields = ['created_at', 'updated_at', 'semanas_edad', 'porcentaje_mortalidad']
    
    fieldsets = (
        ('Información del Lote', {
            'fields': ('codigo', 'galpon', 'linea_genetica', 'procedencia')
        }),
        ('Cantidades', {
            'fields': ('cantidad_inicial', 'cantidad_actual', 'peso_promedio_inicial')
        }),
        ('Fechas', {
            'fields': ('fecha_ingreso', 'fecha_inicio_postura', 'fecha_fin_estimada')
        }),
        ('Estado y Observaciones', {
            'fields': ('estado', 'observaciones')
        }),
        ('Métricas Calculadas', {
            'fields': ('semanas_edad', 'porcentaje_mortalidad'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        colors = {
            'levante': 'orange',
            'postura': 'green',
            'finalizado': 'gray'
        }
        color = colors.get(obj.estado, 'black')
        return format_html(f'<span style="color: {color};">●</span> {obj.get_estado_display()}')
    estado_badge.short_description = 'Estado'


@admin.register(BitacoraDiaria)
class BitacoraDiariaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'total_produccion', 'mortalidad', 'consumo_alimento', 'temperatura', 'humedad']
    list_filter = [FiltroFechaPersonalizado, 'lote', 'lote__galpon']
    search_fields = ['lote__codigo', 'observaciones']
    ordering = ['-fecha']
    readonly_fields = ['created_at', 'updated_at', 'total_produccion']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('fecha', 'lote')
        }),
        ('Producción por Categoría', {
            'fields': ('huevos_aaa', 'huevos_aa', 'huevos_a', 'huevos_b', 'huevos_c', 'total_produccion')
        }),
        ('Mortalidad y Alimento', {
            'fields': ('mortalidad', 'consumo_alimento')
        }),
        ('Condiciones Ambientales', {
            'fields': ('temperatura', 'humedad')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lote', 'lote__galpon')


@admin.register(PollasLevante)
class PollasLevanteAdmin(admin.ModelAdmin):
    list_display = ['lote', 'semana', 'peso_promedio', 'mortalidad_semana', 'consumo_alimento', 'existencias']
    list_filter = ['lote', 'semana', 'lote__galpon']
    search_fields = ['lote__codigo', 'observaciones']
    ordering = ['-lote', '-semana']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('lote', 'semana')
        }),
        ('Métricas de Crecimiento', {
            'fields': ('peso_promedio', 'ganancia_peso')
        }),
        ('Mortalidad y Existencias', {
            'fields': ('mortalidad_semana', 'existencias')
        }),
        ('Consumo', {
            'fields': ('consumo_alimento',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProduccionHuevos)
class ProduccionHuevosAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'total_huevos', 'porcentaje_postura', 'huevos_comerciales', 'created_at']
    list_filter = [FiltroFechaPersonalizado, 'lote', 'lote__galpon']
    search_fields = ['lote__codigo']
    ordering = ['-fecha']
    readonly_fields = ['created_at', 'updated_at', 'total_huevos', 'huevos_comerciales', 'porcentaje_postura']
    date_hierarchy = 'fecha'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lote')


@admin.register(MovimientoHuevos)
class MovimientoHuevosAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'tipo_movimiento', 'categoria_huevo', 'cantidad', 'destino', 'usuario']
    list_filter = ['tipo_movimiento', 'categoria_huevo', 'fecha']
    search_fields = ['destino', 'observaciones', 'usuario__username']
    ordering = ['-fecha']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')


@admin.register(ControlConcentrados)
class ControlConcentradosAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'tipo_movimiento', 'tipo_concentrado', 'cantidad_kg', 'lote', 'stock_actual']
    list_filter = ['tipo_movimiento', 'tipo_concentrado', 'fecha', 'lote']
    search_fields = ['proveedor', 'numero_factura', 'lote__codigo']
    ordering = ['-fecha']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('fecha', 'tipo_movimiento', 'tipo_concentrado')
        }),
        ('Cantidades', {
            'fields': ('cantidad_kg', 'stock_actual')
        }),
        ('Asignación', {
            'fields': ('lote', 'galpon')
        }),
        ('Detalles de Compra', {
            'fields': ('proveedor', 'numero_factura', 'precio_unitario'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlanVacunacion)
class PlanVacunacionAdmin(admin.ModelAdmin):
    list_display = ['vacuna', 'edad_aplicacion_semanas', 'via_aplicacion', 'dosis', 'is_active']
    list_filter = ['via_aplicacion', 'is_active']
    search_fields = ['vacuna', 'descripcion']
    ordering = ['edad_aplicacion_semanas']
    
    fieldsets = (
        ('Información de la Vacuna', {
            'fields': ('vacuna', 'descripcion')
        }),
        ('Aplicación', {
            'fields': ('edad_aplicacion_semanas', 'via_aplicacion', 'dosis')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VacunacionRealizada)
class VacunacionRealizadaAdmin(admin.ModelAdmin):
    list_display = ['fecha_aplicacion', 'lote', 'plan_vacunacion', 'aves_vacunadas', 'veterinario', 'proxima_aplicacion']
    list_filter = ['fecha_aplicacion', 'plan_vacunacion', 'veterinario']
    search_fields = ['lote__codigo', 'plan_vacunacion__vacuna', 'veterinario__username']
    ordering = ['-fecha_aplicacion']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lote', 'plan_vacunacion', 'veterinario')


@admin.register(ControlTemperaturaHumedad)
class ControlTemperaturaHumedadAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'galpon', 'temperatura_promedio', 'humedad_promedio', 'alerta_temperatura', 'alerta_humedad']
    list_filter = [FiltroFechaPersonalizado, 'galpon']
    search_fields = ['galpon__nombre', 'observaciones']
    ordering = ['-fecha']
    readonly_fields = ['created_at', 'updated_at', 'alerta_temperatura', 'alerta_humedad']
    date_hierarchy = 'fecha'
    
    def alerta_temperatura(self, obj):
        if obj.temperatura_minima < 18 or obj.temperatura_maxima > 28:
            return format_html('<span style="color: red;">⚠️ Fuera de rango</span>')
        return format_html('<span style="color: green;">✓ Normal</span>')
    alerta_temperatura.short_description = 'Alerta Temp.'
    
    def alerta_humedad(self, obj):
        if obj.humedad_minima < 50 or obj.humedad_maxima > 70:
            return format_html('<span style="color: red;">⚠️ Fuera de rango</span>')
        return format_html('<span style="color: green;">✓ Normal</span>')
    alerta_humedad.short_description = 'Alerta Hum.'


@admin.register(DespachoHuevos)
class DespachoHuevosAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'numero_comprobante', 'destino', 'total_huevos', 'conductor', 'estado']
    list_filter = ['fecha', 'destino', 'estado']
    search_fields = ['numero_comprobante', 'conductor', 'observaciones']
    ordering = ['-fecha']
    readonly_fields = ['created_at', 'updated_at', 'total_huevos']
    
    fieldsets = (
        ('Información del Despacho', {
            'fields': ('fecha', 'numero_comprobante', 'destino')
        }),
        ('Cantidades por Categoría', {
            'fields': ('huevos_aaa', 'huevos_aa', 'huevos_a', 'huevos_b', 'huevos_c', 'total_huevos')
        }),
        ('Transporte', {
            'fields': ('conductor', 'placa_vehiculo')
        }),
        ('Estado y Observaciones', {
            'fields': ('estado', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AlertasSistema)
class AlertasSistemaAdmin(admin.ModelAdmin):
    list_display = ['tipo_alerta', 'titulo', 'prioridad_badge', 'fecha_creacion', 'leida', 'usuario_destinatario']
    list_filter = ['tipo_alerta', 'prioridad', 'leida', 'fecha_creacion']
    search_fields = ['titulo', 'mensaje', 'usuario_destinatario__username']
    ordering = ['-fecha_creacion']
    readonly_fields = ['created_at', 'updated_at']
    
    def prioridad_badge(self, obj):
        colors = {
            'baja': 'green',
            'media': 'orange',
            'alta': 'red',
            'critica': 'darkred'
        }
        color = colors.get(obj.prioridad, 'black')
        return format_html(f'<span style="color: {color}; font-weight: bold;">●</span> {obj.get_prioridad_display()}')
    prioridad_badge.short_description = 'Prioridad'
    
    actions = ['marcar_como_leidas']
    
    def marcar_como_leidas(self, request, queryset):
        updated = queryset.update(leida=True)
        self.message_user(request, f'{updated} alertas marcadas como leídas.')
    marcar_como_leidas.short_description = "Marcar alertas seleccionadas como leídas"


@admin.register(HistorialCambios)
class HistorialCambiosAdmin(admin.ModelAdmin):
    list_display = ['fecha_cambio', 'usuario', 'modelo', 'accion', 'objeto_id']
    list_filter = ['accion', 'modelo', 'fecha_cambio']
    search_fields = ['usuario__username', 'justificacion', 'objeto_id']
    ordering = ['-fecha_cambio']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Configuración personalizada del sitio admin
admin.site.site_header = "AgroSmart - Administración Avícola"
admin.site.site_title = "AgroSmart Admin"
admin.site.index_title = "Panel de Administración del Módulo Avícola"
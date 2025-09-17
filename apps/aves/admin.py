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
    Galpon, LoteAves, LineaGenetica, BitacoraDiaria, TipoConcentrado,
    ControlConcentrado, TipoVacuna, PlanVacunacion, MovimientoHuevos,
    InventarioHuevos, AlertaSistema, RegistroModificacion
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
    list_display = ['nombre', 'codigo', 'capacidad_maxima', 'tipo_ventilacion', 'is_active']
    list_filter = ['tipo_ventilacion', 'is_active', 'created_at']
    search_fields = ['nombre', 'codigo', 'ubicacion']
    ordering = ['nombre']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'ubicacion')
        }),
        ('Especificaciones', {
            'fields': ('capacidad_maxima', 'area_m2', 'tipo_ventilacion')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LineaGenetica)
class LineaGeneticaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'peso_promedio_adulto', 'produccion_estimada_dia']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

@admin.register(LoteAves)
class LoteAvesAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'galpon', 'linea_genetica', 'numero_aves_inicial', 'numero_aves_actual', 'estado', 'fecha_llegada']
    list_filter = ['galpon', 'linea_genetica', 'estado', 'fecha_llegada']
    search_fields = ['codigo', 'procedencia', 'galpon__nombre']
    ordering = ['-fecha_llegada']
    readonly_fields = ['created_at', 'updated_at', 'edad_dias', 'mortalidad_total', 'porcentaje_mortalidad']

@admin.register(BitacoraDiaria)
class BitacoraDiariaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'lote', 'produccion_total', 'mortalidad', 'consumo_concentrado']
    list_filter = ['fecha', 'lote', 'lote__galpon']
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
    list_display = ['fecha', 'tipo_movimiento', 'tipo_concentrado', 'cantidad_kg', 'lote']
    list_filter = ['tipo_movimiento', 'tipo_concentrado', 'fecha', 'lote']
    search_fields = ['proveedor', 'numero_factura', 'lote__codigo']
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

@admin.register(MovimientoHuevos)
class MovimientoHuevosAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'tipo_movimiento', 'categoria_huevo', 'cantidad', 'cliente']
    list_filter = ['tipo_movimiento', 'categoria_huevo', 'fecha']
    search_fields = ['cliente', 'conductor', 'observaciones']
    ordering = ['-fecha']

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
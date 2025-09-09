from django.contrib import admin
from .models import (
    LoteAves, ProduccionHuevos, CostosProduccion, 
    CalendarioVacunas, Vacunacion, Mortalidad, IndicadorProduccion
)

@admin.register(LoteAves)
class LoteAvesAdmin(admin.ModelAdmin):
    list_display = ['nombre_lote', 'linea', 'cantidad_actual', 'cantidad_aves', 'estado', 'fecha_inicio']
    list_filter = ['linea', 'estado', 'fecha_inicio']
    search_fields = ['nombre_lote', 'observaciones']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre_lote', 'linea', 'fecha_inicio')
        }),
        ('Cantidad de Aves', {
            'fields': ('cantidad_aves', 'cantidad_actual', 'semana_actual')
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProduccionHuevos)
class ProduccionHuevosAdmin(admin.ModelAdmin):
    list_display = ['lote', 'fecha', 'total_huevos', 'porcentaje_postura', 'semana_produccion']
    list_filter = ['fecha', 'semana_produccion', 'lote']
    search_fields = ['lote__nombre_lote']
    readonly_fields = ['created_at', 'updated_at', 'total_huevos', 'porcentaje_postura']
    fieldsets = (
        ('Información Básica', {
            'fields': ('lote', 'fecha', 'semana_produccion', 'numero_aves_produccion')
        }),
        ('Clasificación de Huevos', {
            'fields': ('yumbos', 'extra', 'aa', 'a', 'b', 'c', 'pipo', 'sucios', 'totiados', 'yema')
        }),
        ('Datos Adicionales', {
            'fields': ('peso_promedio_huevo', 'usuario', 'observaciones')
        }),
        ('Métricas Calculadas', {
            'fields': ('total_huevos', 'porcentaje_postura'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(CostosProduccion)
class CostosProduccionAdmin(admin.ModelAdmin):
    list_display = ['lote', 'fecha', 'periodo', 'total_costos', 'total_ingresos', 'utilidad_neta']
    list_filter = ['fecha', 'lote']
    search_fields = ['lote__nombre_lote', 'periodo']
    readonly_fields = ['created_at', 'updated_at', 'total_costos', 'total_ingresos', 'utilidad_neta']
    fieldsets = (
        ('Información Básica', {
            'fields': ('lote', 'fecha', 'periodo')
        }),
        ('Costos', {
            'fields': ('costos_fijos', 'costos_variables', 'gastos_administracion', 'costo_alimento', 'costo_mano_obra', 'otros_costos')
        }),
        ('Ingresos', {
            'fields': ('ingresos_venta_huevos', 'ingresos_venta_aves', 'otros_ingresos')
        }),
        ('Datos Adicionales', {
            'fields': ('usuario', 'observaciones')
        }),
        ('Métricas Calculadas', {
            'fields': ('total_costos', 'total_ingresos', 'utilidad_neta'),
            'classes': ('collapse',)
        })
    )

@admin.register(CalendarioVacunas)
class CalendarioVacunasAdmin(admin.ModelAdmin):
    list_display = ['nombre_vacuna', 'dias_post_nacimiento', 'dosis_ml', 'via_aplicacion', 'obligatoria']
    list_filter = ['obligatoria', 'via_aplicacion']
    search_fields = ['nombre_vacuna', 'descripcion']
    ordering = ['dias_post_nacimiento']

@admin.register(Vacunacion)
class VacunacionAdmin(admin.ModelAdmin):
    list_display = ['lote', 'calendario_vacuna', 'fecha_programada', 'fecha_aplicacion', 'estado', 'responsable']
    list_filter = ['estado', 'fecha_programada', 'fecha_aplicacion']
    search_fields = ['lote__nombre_lote', 'calendario_vacuna__nombre_vacuna', 'responsable']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Mortalidad)
class MortalidadAdmin(admin.ModelAdmin):
    list_display = ['lote', 'fecha', 'cantidad_muertas', 'causa', 'usuario']
    list_filter = ['causa', 'fecha']
    search_fields = ['lote__nombre_lote', 'descripcion_causa']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(IndicadorProduccion)
class IndicadorProduccionAdmin(admin.ModelAdmin):
    list_display = ['lote', 'semana_produccion', 'porcentaje_postura_promedio', 'costo_por_huevo', 'margen_por_huevo']
    list_filter = ['fecha_calculo', 'semana_produccion']
    search_fields = ['lote__nombre_lote']
    readonly_fields = ['fecha_calculo', 'created_at', 'updated_at']
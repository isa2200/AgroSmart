from django.contrib import admin
from .models import LotePorcino, BitacoraDiariaPorcinos, AlertaPorcinos


@admin.register(LotePorcino)
class LotePorcinoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'corral', 'numero_cerdos_actual', 'estado', 'fecha_llegada']
    list_filter = ['estado', 'corral']
    search_fields = ['codigo', 'corral']
    ordering = ['-fecha_llegada']


@admin.register(BitacoraDiariaPorcinos)
class BitacoraDiariaPorcinosAdmin(admin.ModelAdmin):
    list_display = ['lote', 'fecha', 'peso_promedio', 'consumo_alimento_kg', 'mortalidad']
    list_filter = ['fecha', 'lote']
    search_fields = ['lote__codigo']
    ordering = ['-fecha']


@admin.register(AlertaPorcinos)
class AlertaPorcinosAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'lote', 'nivel', 'fecha_generacion', 'leida']
    list_filter = ['nivel', 'leida', 'tipo_alerta', 'fecha_generacion']
    search_fields = ['titulo', 'mensaje', 'lote__codigo']
    date_hierarchy = 'fecha_generacion'

from django.contrib import admin
from .models import (
    InventarioConejos,
    LibroDiarioConejos,
    RegistroAlimentoConejos,
    BitacoraActividadesConejos,
    ControlDestetes
)

@admin.register(InventarioConejos)
class InventarioConejosAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'detalle', 'total', 'gazapos_vivos', 'gazapos_muertos')
    search_fields = ('detalle', 'jaula', 'identificacion')
    list_filter = ('fecha',)

@admin.register(LibroDiarioConejos)
class LibroDiarioConejosAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'parto_jaula', 'parto_vivos', 'monta_jaula', 'destete_jaula')
    list_filter = ('fecha',)

@admin.register(RegistroAlimentoConejos)
class RegistroAlimentoConejosAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'unidad', 'entrada', 'salida', 'saldo')
    list_filter = ('fecha',)

@admin.register(BitacoraActividadesConejos)
class BitacoraActividadesConejosAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'actividad', 'responsable')
    search_fields = ('actividad', 'responsable')
    list_filter = ('fecha',)

@admin.register(ControlDestetes)
class ControlDestetesAdmin(admin.ModelAdmin):
    list_display = ('camada_numero', 'fecha_destete', 'numero_animales', 'madre_numero', 'peso_promedio')
    search_fields = ('camada_numero', 'madre_numero', 'padre_numero')
    list_filter = ('fecha_destete', 'sexo')

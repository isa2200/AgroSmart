from django.contrib import admin
from .models import Lote, Categoria


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_inicio', 'fecha_fin', 'esta_activo', 'is_active', 'created_at']
    list_filter = ['is_active', 'fecha_inicio', 'created_at']
    search_fields = ['nombre', 'descripcion']
    date_hierarchy = 'fecha_inicio'
    
    def esta_activo(self, obj):
        return obj.esta_activo
    esta_activo.boolean = True
    esta_activo.short_description = 'Lote Activo'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nombre', 'descripcion']
from django.contrib import admin
from .models import Equino, RegistroDiario, TratamientoSalud, Novedad, Tarea

@admin.register(Equino)
class EquinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'raza', 'sexo', 'fecha_nacimiento', 'estado')
    search_fields = ('nombre', 'microchip')
    list_filter = ('sexo', 'estado')

@admin.register(RegistroDiario)
class RegistroDiarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'actividad', 'responsable', 'created_at')
    list_filter = ('fecha', 'responsable')
    search_fields = ('actividad', 'observaciones')
    date_hierarchy = 'fecha'

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prioridad', 'estado', 'fecha_limite', 'responsable')
    list_filter = ('prioridad', 'estado', 'responsable')
    search_fields = ('titulo', 'descripcion')

# Register your models here.
admin.site.register(TratamientoSalud)
admin.site.register(Novedad)

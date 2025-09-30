"""
URLs para el módulo avícola.
"""

from django.urls import path
from . import views

app_name = 'aves'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_aves, name='dashboard'),
    
    # Bitácora diaria
    path('bitacora/', views.bitacora_list, name='bitacora_list'),
    path('bitacora/nueva/', views.bitacora_diaria_create, name='bitacora_create'),
    path('bitacora/<int:pk>/', views.bitacora_detail, name='bitacora_detail'),
    path('bitacora/<int:pk>/editar/', views.bitacora_edit, name='bitacora_edit'),
    
    # Lotes
    path('lotes/nuevo/', views.lote_create, name='lote_create'),
    path('lotes/<int:pk>/', views.lote_detail, name='lote_detail'),
    
    # Inventario de huevos
    path('inventario-huevos/', views.inventario_huevos, name='inventario_huevos'),
    path('movimiento-huevos/', views.movimiento_huevos_list, name='movimiento_huevos_list'),
    path('movimiento-huevos/nuevo/', views.movimiento_huevos_create, name='movimiento_huevos_create'),
    
    # Plan de vacunación
    path('vacunacion/', views.plan_vacunacion_list, name='plan_vacunacion_list'),
    path('vacunacion/nuevo/', views.plan_vacunacion_create, name='plan_vacunacion_create'),
    
    # Alertas
    path('alertas/', views.alertas_list, name='alertas_list'),
    path('alertas/<int:pk>/marcar-leida/', views.marcar_alerta_leida, name='marcar_alerta_leida'),
    
    # Reportes
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/produccion/', views.reporte_produccion, name='reporte_produccion'),
]
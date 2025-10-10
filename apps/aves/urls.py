"""
URLs para el módulo avícola.
"""

from django.urls import path
from . import views
from . import views_reports

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
    path('lotes/', views.lote_list, name='lote_list'),
    path('lotes/nuevo/', views.lote_create, name='lote_create'),
    path('lotes/<int:pk>/', views.lote_detail, name='lote_detail'),
    path('lotes/<int:pk>/editar/', views.lote_edit, name='lote_edit'),
    path('lotes/<int:pk>/eliminar/', views.lote_delete, name='lote_delete'),
    
    # Inventario de huevos
    path('inventario-huevos/', views.inventario_huevos, name='inventario_huevos'),
    path('movimiento-huevos/', views.movimiento_huevos_list, name='movimiento_huevos_list'),
    path('movimiento-huevos/nuevo/', views.movimiento_huevos_create, name='movimiento_huevos_create'),
    path('movimiento-huevos/<int:pk>/', views.movimiento_huevos_detail, name='movimiento_huevos_detail'),
    path('actualizar-stock-automatico/', views.actualizar_stock_automatico, name='actualizar_stock_automatico'),
    path('configurar-stock-automatico/<int:inventario_id>/', views.configurar_stock_automatico, name='configurar_stock_automatico'),
    
    # Plan de vacunación
    path('vacunacion/', views.plan_vacunacion_list, name='plan_vacunacion_list'),
    path('vacunacion/nuevo/', views.plan_vacunacion_create, name='plan_vacunacion_create'),
    path('vacunacion/<int:pk>/', views.plan_vacunacion_detail, name='plan_vacunacion_detail'),
    path('vacunacion/<int:pk>/aplicar/', views.plan_vacunacion_aplicar, name='plan_vacunacion_aplicar'),
    
    # Alertas
    path('alertas/', views.alertas_list, name='alertas_list'),
    path('alertas/<int:pk>/marcar-leida/', views.marcar_alerta_leida, name='marcar_alerta_leida'),
    path('alertas/<int:pk>/marcar-resuelta/', views.marcar_alerta_resuelta, name='marcar_alerta_resuelta'),
    path('alertas/marcar-masivo/', views.marcar_alertas_masivo, name='marcar_alertas_masivo'),
    
    # Reportes
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/dashboard/', views_reports.dashboard_reportes, name='reportes_dashboard'),
    path('reportes/produccion/', views.reporte_produccion, name='reporte_produccion'),
    path('reportes/mortalidad/', views_reports.reporte_mortalidad, name='reporte_mortalidad'),
    path('reportes/consumo/', views_reports.reporte_consumo_concentrado, name='reporte_consumo'),
    path('reportes/vacunacion/', views_reports.reporte_salud_vacunacion, name='reporte_vacunacion'),
    path('reportes/comparativo-lotes/', views_reports.reporte_comparativo_lotes, name='reporte_comparativo_lotes'),
    path('reportes/exportar-completo/', views_reports.exportar_datos_completos, name='exportar_datos_completos'),
    path('api/datos-dashboard/', views_reports.api_datos_dashboard, name='api_datos_dashboard'),
]
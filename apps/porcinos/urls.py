from django.urls import path
from . import views

app_name = 'porcinos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('lotes/', views.lote_list, name='lote_list'),
    path('lotes/nuevo/', views.lote_create, name='lote_create'),
    path('lotes/<int:pk>/', views.lote_detail, name='lote_detail'),
    path('lotes/<int:pk>/editar/', views.lote_edit, name='lote_edit'),
    path('lotes/<int:pk>/eliminar/', views.lote_delete, name='lote_delete'),
    path('bitacora/', views.bitacora_list, name='bitacora_list'),
    path('bitacora/nueva/', views.bitacora_create, name='bitacora_create'),
    path('bitacora/<int:pk>/', views.bitacora_detail, name='bitacora_detail'),
    path('bitacora/<int:pk>/editar/', views.bitacora_update, name='bitacora_update'),
    path('inventario/permanente/', views.inventario_permanente, name='inventario_permanente'),
    path('registro/alimento/', views.registro_alimento, name='registro_alimento'),
    path('plan/gestante/', views.plan_sanitario_gestante, name='plan_gestante'),
    path('alertas/', views.alertas_list, name='alertas_list'),
    path('alertas/<int:alerta_id>/leida/', views.marcar_alerta_leida, name='marcar_alerta_leida'),
    path('alertas/masivo/', views.marcar_alertas_masivo, name='marcar_alertas_masivo'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/produccion/', views.reporte_produccion, name='reporte_produccion'),
    
    # Animales
    path('animales/', views.animal_list, name='animal_list'),
    path('animales/nuevo/', views.animal_create, name='animal_create'),
    path('animales/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animales/<int:pk>/editar/', views.animal_update, name='animal_update'),
    path('animales/<int:pk>/eliminar/', views.animal_delete, name='animal_delete'),
    
    # Tareas
    path('tarea/crear/', views.crear_tarea, name='crear_tarea'),
    path('tarea/<int:tarea_id>/completar/', views.completar_tarea, name='completar_tarea'),
    path('tarea/<int:tarea_id>/eliminar/', views.eliminar_tarea, name='eliminar_tarea'),
    
    # Plan de Vacunación
    path('plan-vacunacion/', views.plan_vacunacion_list, name='plan_vacunacion_list'),
    path('plan-vacunacion/nuevo/', views.plan_vacunacion_create, name='plan_vacunacion_create'),
    path('plan-vacunacion/<int:pk>/editar/', views.plan_vacunacion_update, name='plan_vacunacion_update'),
    path('plan-vacunacion/<int:pk>/eliminar/', views.plan_vacunacion_delete, name='plan_vacunacion_delete'),
]

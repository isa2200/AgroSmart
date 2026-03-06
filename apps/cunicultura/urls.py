from django.urls import path
from . import views

app_name = 'cunicultura'

urlpatterns = [
    path('', views.dashboard_cunicultura, name='dashboard'),
    path('inventario/', views.inventario_permanente, name='inventario_permanente'),
    path('inventario/historial/', views.historial_inventario, name='historial_inventario'),
    path('libro-diario/', views.libro_diario, name='libro_diario'),
    path('control-destetes/', views.control_destetes, name='control_destetes'),
    path('registro-alimento/', views.registro_alimento, name='registro_alimento'),
    path('bitacora-actividades/', views.bitacora_actividades, name='bitacora_actividades'),
    # Tareas
    path('tarea/crear/', views.crear_tarea, name='crear_tarea'),
    path('tarea/completar/<int:tarea_id>/', views.completar_tarea, name='completar_tarea'),
    path('tarea/eliminar/<int:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),

    # Plan de Vacunación
    path('plan-vacunacion/', views.plan_vacunacion_list, name='plan_vacunacion_list'),
    path('plan-vacunacion/nuevo/', views.plan_vacunacion_create, name='plan_vacunacion_create'),
    path('plan-vacunacion/<int:pk>/editar/', views.plan_vacunacion_update, name='plan_vacunacion_update'),
    path('plan-vacunacion/<int:pk>/eliminar/', views.plan_vacunacion_delete, name='plan_vacunacion_delete'),
]

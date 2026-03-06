from django.urls import path
from . import views

app_name = 'equinos'

urlpatterns = [
    path('', views.dashboard_equinos, name='dashboard'),
    
    # Equinos
    path('equinos/', views.equino_list, name='equino_list'),
    path('equinos/crear/', views.crear_equino, name='crear_equino'),
    path('equinos/detalle/<int:equino_id>/', views.equino_detail, name='equino_detail'),
    path('equinos/editar/<int:equino_id>/', views.equino_update, name='equino_update'),
    
    # Registro Diario
    path('registro_diario/crear/', views.crear_registro_diario, name='crear_registro_diario'),
    
    path('tarea/crear/', views.crear_tarea, name='crear_tarea'),
    path('tarea/completar/<int:tarea_id>/', views.completar_tarea, name='completar_tarea'),
    path('tarea/eliminar/<int:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),

    # Plan de Vacunación
    path('plan-vacunacion/', views.plan_vacunacion_list, name='plan_vacunacion_list'),
    path('plan-vacunacion/nuevo/', views.plan_vacunacion_create, name='plan_vacunacion_create'),
    path('plan-vacunacion/<int:pk>/editar/', views.plan_vacunacion_update, name='plan_vacunacion_update'),
    path('plan-vacunacion/<int:pk>/eliminar/', views.plan_vacunacion_delete, name='plan_vacunacion_delete'),
]

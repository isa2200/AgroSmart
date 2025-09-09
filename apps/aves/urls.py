from django.urls import path
from . import views

app_name = 'aves'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_aves, name='dashboard'),
    
    # Lotes
    path('lotes/', views.lista_lotes, name='lista_lotes'),
    path('lotes/crear/', views.crear_lote, name='crear_lote'),
    path('lotes/<int:pk>/editar/', views.editar_lote, name='editar_lote'),
    path('lotes/<int:pk>/eliminar/', views.eliminar_lote, name='eliminar_lote'),
    
    # Producción
    path('produccion/', views.lista_produccion, name='lista_produccion'),
    path('produccion/crear/', views.crear_produccion, name='crear_produccion'),
    path('produccion/<int:pk>/editar/', views.editar_produccion, name='editar_produccion'),
    path('produccion/<int:pk>/eliminar/', views.eliminar_produccion, name='eliminar_produccion'),
    
    # Costos
    path('costos/', views.lista_costos, name='lista_costos'),
    path('costos/crear/', views.crear_costo, name='crear_costo'),
    path('costos/<int:pk>/editar/', views.editar_costo, name='editar_costo'),
    path('costos/<int:pk>/eliminar/', views.eliminar_costo, name='eliminar_costo'),
    
    # Vacunación
    path('vacunacion/', views.lista_vacunacion, name='lista_vacunacion'),
    path('vacunacion/crear/', views.crear_vacunacion, name='crear_vacunacion'),
    path('vacunacion/<int:pk>/editar/', views.editar_vacunacion, name='editar_vacunacion'),
    path('vacunacion/<int:pk>/eliminar/', views.eliminar_vacunacion, name='eliminar_vacunacion'),
    
    # Mortalidad
    path('mortalidad/', views.lista_mortalidad, name='lista_mortalidad'),
    path('mortalidad/crear/', views.crear_mortalidad, name='crear_mortalidad'),
    path('mortalidad/<int:pk>/editar/', views.editar_mortalidad, name='editar_mortalidad'),
    path('mortalidad/<int:pk>/eliminar/', views.eliminar_mortalidad, name='eliminar_mortalidad'),
    
    # APIs para gráficos
    path('api/produccion-semanal/', views.api_produccion_semanal, name='api_produccion_semanal'),
    path('api/costos-mensuales/', views.api_costos_mensuales, name='api_costos_mensuales'),
    path('api/indicadores/', views.api_indicadores, name='api_indicadores'),
]
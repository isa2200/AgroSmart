from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_principal, name='principal'),
    path('api/produccion/', views.datos_graficos_produccion, name='api_produccion'),
    path('api/inventario/', views.datos_inventario_animales, name='api_inventario'),
    path('api/unidad/usuarios/', views.obtener_usuarios_unidad, name='api_usuarios_unidad'),
    path('api/unidad/agregar-usuario/', views.agregar_usuario_unidad, name='api_agregar_usuario'),
]
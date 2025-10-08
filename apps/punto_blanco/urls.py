from django.urls import path
from . import views

app_name = 'punto_blanco'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_punto_blanco, name='dashboard'),
    
    # Pedidos
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/crear/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/<int:pk>/cambiar-estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    
    # Inventario
    path('inventario/', views.inventario_punto_blanco, name='inventario'),
    
    # Configuración
    path('configuracion/', views.configuracion_punto_blanco, name='configuracion'),
    
    # API
    path('api/inventario/<int:inventario_id>/', views.api_inventario_info, name='api_inventario_info'),
]
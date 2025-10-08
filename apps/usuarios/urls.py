"""
URLs para la app de usuarios.
"""

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('editar-perfil/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    # Gestión de usuarios (solo superusuarios)
    path('lista/', views.UsuarioListView.as_view(), name='lista'),
    path('crear/', views.CrearUsuarioView.as_view(), name='crear'),
    path('detalle/<int:pk>/', views.UsuarioDetailView.as_view(), name='detalle'),
    path('editar/<int:pk>/', views.EditarUsuarioView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', views.EliminarUsuarioView.as_view(), name='eliminar'),
    # Punto Blanco - Inventarios
    path('punto-blanco/', views.PuntoBlancoDashboardView.as_view(), name='punto_blanco_dashboard'),
    path('punto-blanco/inventario-huevos/', views.PuntoBlancoInventarioHuevosView.as_view(), name='punto_blanco_inventario_huevos'),
]
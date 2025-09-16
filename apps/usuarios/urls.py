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
    path('lista/', views.UsuarioListView.as_view(), name='lista'),
    path('crear/', views.CrearUsuarioView.as_view(), name='crear'),
]
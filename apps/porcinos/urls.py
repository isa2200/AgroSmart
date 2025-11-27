from django.urls import path
from . import views

app_name = 'porcinos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('lotes/', views.lote_list, name='lote_list'),
    path('lotes/nuevo/', views.lote_create, name='lote_create'),
    path('bitacora/', views.bitacora_list, name='bitacora_list'),
    path('bitacora/nueva/', views.bitacora_create, name='bitacora_create'),
]

from django.urls import path
from . import views

app_name = 'cunicultura'

urlpatterns = [
    path('', views.dashboard_cunicultura, name='dashboard'),
    path('inventario/', views.inventario_permanente, name='inventario_permanente'),
    path('libro-diario/', views.libro_diario, name='libro_diario'),
]

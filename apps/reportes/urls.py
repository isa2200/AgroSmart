"""
URLs para la aplicación de reportes en AgroSmart.
"""

from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # URLs básicas para reportes
    path('', views.lista_reportes, name='lista_reportes'),
    path('produccion/', views.reporte_produccion, name='reporte_produccion'),
    path('financiero/', views.reporte_financiero, name='reporte_financiero'),
    path('sanitario/', views.reporte_sanitario, name='reporte_sanitario'),
    
    # APIs para datos de reportes
    path('api/datos-produccion/', views.api_datos_produccion, name='api_datos_produccion'),
    path('api/datos-financieros/', views.api_datos_financieros, name='api_datos_financieros'),
]
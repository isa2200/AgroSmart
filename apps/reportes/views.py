"""
Vistas para la aplicación de reportes en AgroSmart.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
from django.utils import timezone

from apps.aves.models import LoteAves, ProduccionHuevos, CostosProduccion, Mortalidad


@login_required
def lista_reportes(request):
    """
    Vista principal de reportes - lista de reportes disponibles
    """
    context = {
        'titulo': 'Reportes del Sistema',
        'reportes_disponibles': [
            {'nombre': 'Reporte de Producción', 'url': 'reportes:reporte_produccion'},
            {'nombre': 'Reporte Financiero', 'url': 'reportes:reporte_financiero'},
            {'nombre': 'Reporte Sanitario', 'url': 'reportes:reporte_sanitario'},
        ]
    }
    return render(request, 'reportes/lista_reportes.html', context)


@login_required
def reporte_produccion(request):
    """
    Reporte de producción de huevos
    """
    # Datos básicos de producción
    lotes_activos = LoteAves.objects.filter(estado='activo')
    
    # Producción del último mes
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    produccion_mes = ProduccionHuevos.objects.filter(
        fecha__gte=fecha_inicio
    ).aggregate(
        total_huevos=Sum('yumbos') + Sum('extra') + Sum('aa') + Sum('a') + Sum('b') + Sum('c'),
        promedio_postura=Avg('numero_aves_produccion')
    )
    
    context = {
        'titulo': 'Reporte de Producción',
        'lotes_activos': lotes_activos,
        'produccion_mes': produccion_mes,
        'fecha_reporte': timezone.now().date()
    }
    return render(request, 'reportes/produccion.html', context)

# REPORTE DE PRODUCCIÓN SEMANAL
def reporte_produccion_semanal(lote_id, fecha_inicio, fecha_fin):
    """
    Fórmulas:
    - Total huevos = Sum(yumbos + extra + aa + a + b + c + pipo + sucios + totiados + yema)
    - Huevos comerciales = Sum(yumbos + extra + aa + a + b + c)
    - % Postura promedio = (Total huevos / Aves promedio en producción) * 100
    - Peso promedio = Avg(peso_promedio_huevo)
    - Gramos/ave/día = (Peso promedio * Total huevos) / Aves promedio
    """
    return {
        'periodo': f'{fecha_inicio} - {fecha_fin}',
        'total_huevos': 6850,  # Ejemplo
        'huevos_comerciales': 6520,
        'porcentaje_comerciales': 95.18,
        'porcentaje_postura_promedio': 89.5,
        'peso_promedio_huevo': 61.2,
        'gramos_ave_dia': 54.8,
        'aves_promedio_produccion': 945
    }


@login_required
def reporte_financiero(request):
    """
    Reporte financiero de costos e ingresos
    """
    # Costos del último mes
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    costos_mes = CostosProduccion.objects.filter(
        fecha__gte=fecha_inicio
    ).aggregate(
        total_costos=Sum('costos_fijos') + Sum('costos_variables'),
        total_ingresos=Sum('ingresos_venta_huevos') + Sum('ingresos_venta_aves')
    )
    
    context = {
        'titulo': 'Reporte Financiero',
        'costos_mes': costos_mes,
        'fecha_reporte': timezone.now().date()
    }
    return render(request, 'reportes/financiero.html', context)

# REPORTE FINANCIERO MENSUAL
def reporte_financiero_mensual(lote_id, mes, año):
    """
    Fórmulas:
    - Ingresos totales = Sum(ingresos_venta_huevos + ingresos_venta_aves + otros_ingresos)
    - Costos totales = Sum(costos_fijos + costos_variables + costo_alimento + costo_mano_obra)
    - Utilidad neta = Ingresos totales - Costos totales
    - Margen utilidad = (Utilidad neta / Ingresos totales) * 100
    - Costo por huevo = Costos totales / Total huevos producidos
    - Ingreso por huevo = Ingresos huevos / Total huevos vendidos
    """
    return {
        'periodo': f'{mes}/{año}',
        'ingresos_totales': 15750.00,  # Ejemplo USD
        'costos_totales': 12300.00,
        'utilidad_neta': 3450.00,
        'margen_utilidad': 21.9,
        'costo_por_huevo': 0.45,
        'ingreso_por_huevo': 0.58,
        'roi_mensual': 28.0
    }


# REPORTE DE INDICADORES ZOOTÉCNICOS
def reporte_indicadores_zootecnicos(lote_id):
    """
    Fórmulas estándar de la industria:
    - Mortalidad acumulada = ((Aves iniciales - Aves actuales) / Aves iniciales) * 100
    - Conversión alimenticia = Kg alimento consumido / Kg huevos producidos
    - Huevos por ave alojada = Total huevos / Aves iniciales
    - Huevos por ave día = Total huevos / (Aves promedio * Días)
    - Pico de producción = Máximo % postura alcanzado
    - Persistencia = Semanas con >80% postura
    """
    return {
        'edad_lote_semanas': 28,
        'mortalidad_acumulada': 5.5,
        'porcentaje_postura_actual': 89.2,
        'pico_produccion': 94.8,
        'persistencia_semanas': 12,
        'huevos_ave_alojada': 156.8,
        'conversion_alimenticia': 2.1,
        'peso_corporal_promedio': 1850  # gramos
    }
@login_required
def reporte_sanitario(request):
    """
    Reporte sanitario - mortalidad y vacunaciones
    """
    # Mortalidad del último mes
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    mortalidad_mes = Mortalidad.objects.filter(
        fecha__gte=fecha_inicio
    ).aggregate(
        total_muertes=Sum('cantidad_muertas'),
        casos_enfermedad=Count('id', filter=Q(causa='enfermedad'))
    )
    
    context = {
        'titulo': 'Reporte Sanitario',
        'mortalidad_mes': mortalidad_mes,
        'fecha_reporte': timezone.now().date()
    }
    return render(request, 'reportes/sanitario.html', context)


# APIs para datos de reportes
@login_required
def api_datos_produccion(request):
    """
    API para obtener datos de producción en formato JSON
    """
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    producciones = ProduccionHuevos.objects.filter(
        fecha__gte=fecha_inicio
    ).values('fecha', 'lote__nombre_lote').annotate(
        total_huevos=Sum('yumbos') + Sum('extra') + Sum('aa') + Sum('a') + Sum('b') + Sum('c')
    )
    
    data = list(producciones)
    return JsonResponse({'producciones': data})


@login_required
def api_datos_financieros(request):
    """
    API para obtener datos financieros en formato JSON
    """
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    costos = CostosProduccion.objects.filter(
        fecha__gte=fecha_inicio
    ).values('fecha', 'lote__nombre_lote').annotate(
        total_costos=Sum('costos_fijos') + Sum('costos_variables'),
        total_ingresos=Sum('ingresos_venta_huevos') + Sum('ingresos_venta_aves')
    )
    
    data = list(costos)
    return JsonResponse({'costos': data})
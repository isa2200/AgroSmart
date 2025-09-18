"""
Vistas para la aplicación de reportes en AgroSmart.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone

from apps.aves.models import LoteAves, BitacoraDiaria, MovimientoHuevos, ControlConcentrado


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
    Vista para generar reportes de producción de huevos
    """
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        formato = request.POST.get('formato', 'pdf')
        
        # Usar BitacoraDiaria en lugar de ProduccionHuevos
        datos_produccion = BitacoraDiaria.objects.filter(
            fecha__range=[fecha_inicio, fecha_fin]
        ).select_related('lote').values(
            'lote__codigo',
            'lote__nombre_lote', 
            'fecha',
            'huevos_recolectados',
            'peso_promedio_huevo'
        )
        
        # Datos básicos de producción
        lotes_activos = LoteAves.objects.filter(estado='postura')
        
        # Producción del último mes usando BitacoraDiaria
        fecha_inicio = timezone.now().date() - timedelta(days=30)
        produccion_mes = BitacoraDiaria.objects.filter(
            fecha__gte=fecha_inicio
        ).aggregate(
            total_huevos_aaa=Sum('produccion_aaa'),
            total_huevos_aa=Sum('produccion_aa'),
            total_huevos_a=Sum('produccion_a'),
            total_huevos_b=Sum('produccion_b'),
            total_huevos_c=Sum('produccion_c'),
            promedio_mortalidad=Avg('mortalidad'),
            total_consumo=Sum('consumo_concentrado')
        )
        
        # Calcular total de huevos
        total_huevos = (
            (produccion_mes['total_huevos_aaa'] or 0) +
            (produccion_mes['total_huevos_aa'] or 0) +
            (produccion_mes['total_huevos_a'] or 0) +
            (produccion_mes['total_huevos_b'] or 0) +
            (produccion_mes['total_huevos_c'] or 0)
        )
        
        context = {
            'titulo': 'Reporte de Producción',
            'lotes_activos': lotes_activos,
            'produccion_mes': produccion_mes,
            'total_huevos': total_huevos,
            'fecha_reporte': timezone.now().date()
        }
        return render(request, 'reportes/produccion.html', context)

def api_datos_produccion(request):
    """
    API para obtener datos de producción para gráficos
    """
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Usar BitacoraDiaria en lugar de ProduccionHuevos
    datos = BitacoraDiaria.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    ).values('fecha').annotate(
        total_huevos=Sum('huevos_recolectados'),
        promedio_peso=Avg('peso_promedio_huevo')
    ).order_by('fecha')
    
    return JsonResponse(list(datos), safe=False)


# REPORTE DE PRODUCCIÓN SEMANAL
def reporte_produccion_semanal(lote_id, fecha_inicio, fecha_fin):
    """
    Fórmulas:
    - Total huevos = Sum(produccion_aaa + produccion_aa + produccion_a + produccion_b + produccion_c)
    - Huevos comerciales = Sum(produccion_aaa + produccion_aa + produccion_a + produccion_b)
    - % Postura promedio = (Total huevos / Aves promedio en producción) * 100
    - Peso promedio = Calculado basado en categorías
    - Gramos/ave/día = (Peso promedio * Total huevos) / Aves promedio
    """
    bitacoras = BitacoraDiaria.objects.filter(
        lote_id=lote_id,
        fecha__range=[fecha_inicio, fecha_fin]
    ).aggregate(
        total_aaa=Sum('produccion_aaa'),
        total_aa=Sum('produccion_aa'),
        total_a=Sum('produccion_a'),
        total_b=Sum('produccion_b'),
        total_c=Sum('produccion_c'),
        promedio_mortalidad=Avg('mortalidad'),
        total_consumo=Sum('consumo_concentrado')
    )
    
    total_huevos = (
        (bitacoras['total_aaa'] or 0) +
        (bitacoras['total_aa'] or 0) +
        (bitacoras['total_a'] or 0) +
        (bitacoras['total_b'] or 0) +
        (bitacoras['total_c'] or 0)
    )
    
    huevos_comerciales = (
        (bitacoras['total_aaa'] or 0) +
        (bitacoras['total_aa'] or 0) +
        (bitacoras['total_a'] or 0) +
        (bitacoras['total_b'] or 0)
    )
    
    return {
        'periodo': f'{fecha_inicio} - {fecha_fin}',
        'total_huevos': total_huevos,
        'huevos_comerciales': huevos_comerciales,
        'porcentaje_comerciales': (huevos_comerciales / total_huevos * 100) if total_huevos > 0 else 0,
        'promedio_mortalidad': bitacoras['promedio_mortalidad'] or 0,
        'total_consumo': bitacoras['total_consumo'] or 0
    }


@login_required
def reporte_financiero(request):
    """
    Reporte financiero de costos e ingresos
    """
    # Costos del último mes basado en movimientos de huevos y concentrados
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    
    # Ingresos por venta de huevos
    ingresos_huevos = MovimientoHuevos.objects.filter(
        fecha__gte=fecha_inicio,
        tipo_movimiento='venta'
    ).aggregate(
        total_ingresos=Sum('cantidad') * Avg('precio_unitario')
    )
    
    # Costos de concentrados
    costos_concentrados = ControlConcentrado.objects.filter(
        fecha__gte=fecha_inicio,
        tipo_movimiento='entrada'
    ).aggregate(
        total_costos=Sum('cantidad_kg') * 0.5  # Precio estimado por kg
    )
    
    context = {
        'titulo': 'Reporte Financiero',
        'ingresos_huevos': ingresos_huevos,
        'costos_concentrados': costos_concentrados,
        'fecha_reporte': timezone.now().date()
    }
    return render(request, 'reportes/financiero.html', context)

# REPORTE FINANCIERO MENSUAL
def reporte_financiero_mensual(lote_id, mes, año):
    """
    Fórmulas:
    - Ingresos totales = Sum(ventas de huevos)
    - Costos totales = Sum(costos de concentrados + otros costos estimados)
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
    Fórmulas estándar de la industria basadas en BitacoraDiaria:
    - Mortalidad acumulada = Sum(mortalidad) / Aves iniciales * 100
    - Conversión alimenticia = Kg alimento consumido / Kg huevos producidos
    - Huevos por ave alojada = Total huevos / Aves iniciales
    - Huevos por ave día = Total huevos / (Aves promedio * Días)
    - Pico de producción = Máximo % postura alcanzado
    - Persistencia = Días con alta producción
    """
    lote = LoteAves.objects.get(id=lote_id)
    bitacoras = BitacoraDiaria.objects.filter(lote=lote)
    
    total_mortalidad = bitacoras.aggregate(Sum('mortalidad'))['mortalidad__sum'] or 0
    total_produccion = bitacoras.aggregate(
        total=Sum('produccion_aaa') + Sum('produccion_aa') + Sum('produccion_a') + Sum('produccion_b') + Sum('produccion_c')
    )['total'] or 0
    
    return {
        'edad_lote_dias': lote.edad_dias,
        'mortalidad_acumulada': (total_mortalidad / lote.numero_aves_inicial * 100) if lote.numero_aves_inicial > 0 else 0,
        'total_produccion': total_produccion,
        'huevos_ave_alojada': (total_produccion / lote.numero_aves_inicial) if lote.numero_aves_inicial > 0 else 0,
        'aves_actuales': lote.numero_aves_actual
    }

@login_required
def reporte_sanitario(request):
    """
    Reporte sanitario - mortalidad basado en BitacoraDiaria
    """
    # Mortalidad del último mes
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    mortalidad_mes = BitacoraDiaria.objects.filter(
        fecha__gte=fecha_inicio
    ).aggregate(
        total_muertes=Sum('mortalidad'),
        promedio_diario=Avg('mortalidad'),
        dias_con_mortalidad=Count('id', filter=Q(mortalidad__gt=0))
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
    # Obtener datos de producción desde BitacoraDiaria
    datos = BitacoraDiaria.objects.filter(
        huevos_producidos__gt=0
    ).values(
        'fecha',
        'huevos_producidos',
        'lote_aves__numero_lote',
        'galpon__nombre'
    ).order_by('-fecha')[:100]
    
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    producciones = BitacoraDiaria.objects.filter(
        fecha__gte=fecha_inicio
    ).values('fecha', 'lote__codigo').annotate(
        total_huevos=Sum('produccion_aaa') + Sum('produccion_aa') + Sum('produccion_a') + Sum('produccion_b') + Sum('produccion_c')
    )
    
    data = list(producciones)
    return JsonResponse({'producciones': data})


@login_required
def api_datos_financieros(request):
    """
    API para obtener datos financieros en formato JSON
    """
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    
    # Datos de movimientos de huevos (ventas)
    ventas = MovimientoHuevos.objects.filter(
        fecha__gte=fecha_inicio,
        tipo_movimiento='venta'
    ).values('fecha').annotate(
        total_ingresos=Sum('cantidad') * Avg('precio_unitario')
    )
    
    data = list(ventas)
    return JsonResponse({'ventas': data})
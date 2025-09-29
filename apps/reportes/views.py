"""
Vistas para el módulo de reportes.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone

from apps.aves.models import LoteAves, BitacoraDiaria, MovimientoHuevos, ControlConcentrado


@login_required
def lista_reportes(request):
    """Lista de reportes disponibles."""
    reportes = [
        {'nombre': 'Producción', 'url': 'reportes:produccion', 'descripcion': 'Reporte de producción de huevos'},
        {'nombre': 'Financiero', 'url': 'reportes:financiero', 'descripcion': 'Reporte financiero'},
        {'nombre': 'Sanitario', 'url': 'reportes:sanitario', 'descripcion': 'Reporte sanitario'},
    ]
    
    context = {
        'reportes': reportes
    }
    
    return render(request, 'reportes/lista_reportes.html', context)

@login_required
def reporte_produccion(request):
    """Reporte de producción."""
    # Obtener parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    lote_id = request.GET.get('lote')
    
    # Filtros por defecto (último mes)
    if not fecha_inicio:
        fecha_inicio = (timezone.now() - timedelta(days=30)).date()
    else:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    if not fecha_fin:
        fecha_fin = timezone.now().date()
    else:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    # Construir filtros
    filtros = {
        'fecha__range': [fecha_inicio, fecha_fin]
    }
    
    if lote_id:
        filtros['lote_id'] = lote_id
    
    # Obtener datos
    bitacoras = BitacoraDiaria.objects.filter(**filtros).select_related('lote')
    
    # Estadísticas
    estadisticas = bitacoras.aggregate(
        total_produccion=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')),
        total_mortalidad=Sum('mortalidad'),
        promedio_consumo=Avg('consumo_concentrado')
    )
    
    # Lotes para el filtro
    lotes = LoteAves.objects.filter(is_active=True)
    
    context = {
        'bitacoras': bitacoras,
        'estadisticas': estadisticas,
        'lotes': lotes,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'lote_seleccionado': lote_id,
    }
    
    return render(request, 'reportes/reporte_produccion.html', context)

def api_datos_produccion(request):
    """API para datos de producción."""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if not fecha_inicio or not fecha_fin:
        return JsonResponse({'error': 'Fechas requeridas'}, status=400)
    
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    # Usar BitacoraDiaria en lugar de ProduccionHuevos
    datos = BitacoraDiaria.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin]
    ).values('fecha').annotate(
        total_huevos=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c'))
    ).order_by('fecha')
    
    return JsonResponse(list(datos), safe=False)


def reporte_produccion_semanal(lote_id, fecha_inicio, fecha_fin):
    """Genera reporte de producción semanal."""
    filtros = {
        'fecha__range': [fecha_inicio, fecha_fin]
    }
    
    if lote_id:
        filtros['lote_id'] = lote_id
    
    # Obtener datos de producción
    produccion = BitacoraDiaria.objects.filter(**filtros).select_related('lote')
    
    # Agrupar por semana
    datos_semanales = {}
    for bitacora in produccion:
        # Calcular número de semana
        semana = bitacora.fecha.isocalendar()[1]
        año = bitacora.fecha.year
        clave_semana = f"{año}-S{semana:02d}"
        
        if clave_semana not in datos_semanales:
            datos_semanales[clave_semana] = {
                'semana': clave_semana,
                'total_huevos': 0,
                'total_mortalidad': 0,
                'total_consumo': 0,
                'dias_registrados': 0
            }
        
        datos_semanales[clave_semana]['total_huevos'] += bitacora.produccion_total
        datos_semanales[clave_semana]['total_mortalidad'] += bitacora.mortalidad
        datos_semanales[clave_semana]['total_consumo'] += bitacora.consumo_concentrado or 0
        datos_semanales[clave_semana]['dias_registrados'] += 1
    
    # Convertir a lista y calcular promedios
    resultado = []
    for datos in datos_semanales.values():
        datos['promedio_huevos_dia'] = datos['total_huevos'] / datos['dias_registrados'] if datos['dias_registrados'] > 0 else 0
        datos['promedio_mortalidad_dia'] = datos['total_mortalidad'] / datos['dias_registrados'] if datos['dias_registrados'] > 0 else 0
        datos['promedio_consumo_dia'] = datos['total_consumo'] / datos['dias_registrados'] if datos['dias_registrados'] > 0 else 0
        resultado.append(datos)
    
    return {
        'datos_semanales': sorted(resultado, key=lambda x: x['semana']),
        'resumen': {
            'total_semanas': len(resultado),
            'total_huevos': sum(d['total_huevos'] for d in resultado),
            'total_mortalidad': sum(d['total_mortalidad'] for d in resultado),
            'total_consumo': sum(d['total_consumo'] for d in resultado)
        }
    }


@login_required
def reporte_financiero(request):
    """Reporte financiero."""
    # Obtener parámetros
    mes = request.GET.get('mes', timezone.now().month)
    año = request.GET.get('año', timezone.now().year)
    lote_id = request.GET.get('lote')
    
    # Generar datos del reporte
    datos = reporte_financiero_mensual(lote_id, mes, año)
    
    # Lotes para filtro
    lotes = LoteAves.objects.filter(is_active=True)
    
    context = {
        'datos': datos,
        'lotes': lotes,
        'mes_seleccionado': int(mes),
        'año_seleccionado': int(año),
        'lote_seleccionado': lote_id,
    }
    
    return render(request, 'reportes/reporte_financiero.html', context)


def reporte_financiero_mensual(lote_id, mes, año):
    """Genera datos del reporte financiero mensual."""
    # Aquí implementarías la lógica para calcular ingresos, gastos, etc.
    # Por ahora retornamos datos de ejemplo
    
    return {
        'ingresos_ventas': 50000,
        'gastos_concentrado': 15000,
        'gastos_medicamentos': 2000,
        'gastos_otros': 3000,
        'utilidad_neta': 30000,
        'margen_utilidad': 60.0
    }


def reporte_indicadores_zootecnicos(lote_id):
    """Calcula indicadores zootécnicos para un lote."""
    try:
        lote = LoteAves.objects.get(id=lote_id)
        
        # Obtener bitácoras del lote
        bitacoras = BitacoraDiaria.objects.filter(lote=lote).order_by('fecha')
        
        if not bitacoras.exists():
            return None
        
        # Calcular indicadores
        total_produccion = sum(b.produccion_total for b in bitacoras)
        total_mortalidad = sum(b.mortalidad for b in bitacoras)
        dias_produccion = bitacoras.count()
        
        return {
            'lote': lote.codigo,
            'total_produccion': total_produccion,
            'total_mortalidad': total_mortalidad,
            'dias_produccion': dias_produccion,
            'promedio_produccion_dia': total_produccion / dias_produccion if dias_produccion > 0 else 0,
            'porcentaje_mortalidad': (total_mortalidad / lote.cantidad_inicial) * 100 if lote.cantidad_inicial > 0 else 0,
            'aves_actuales': lote.numero_aves_actual
        }
        
    except LoteAves.DoesNotExist:
        return None

@login_required
def reporte_sanitario(request):
    """Reporte sanitario."""
    # Obtener parámetros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = (timezone.now() - timedelta(days=30)).date()
    else:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    if not fecha_fin:
        fecha_fin = timezone.now().date()
    else:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'reportes/reporte_sanitario.html', context)

@login_required
def api_datos_produccion(request):
    """API para obtener datos de producción para gráficos."""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    lote_id = request.GET.get('lote_id')
    
    if not fecha_inicio or not fecha_fin:
        return JsonResponse({'error': 'Fechas requeridas'}, status=400)
    
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    filtros = {'fecha__range': [fecha_inicio, fecha_fin]}
    if lote_id:
        filtros['lote_id'] = lote_id
    
    datos = BitacoraDiaria.objects.filter(**filtros).values(
        'fecha', 'lote__codigo'
    ).annotate(
        total_produccion=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')),
        mortalidad=Sum('mortalidad')
    ).order_by('fecha')
    
    return JsonResponse(list(datos), safe=False)

@login_required
def api_datos_financieros(request):
    """API para datos financieros."""
    # Datos de ejemplo - implementar lógica real según necesidades
    data = [
        {'mes': 'Enero', 'ingresos': 45000, 'gastos': 20000},
        {'mes': 'Febrero', 'ingresos': 52000, 'gastos': 22000},
        {'mes': 'Marzo', 'ingresos': 48000, 'gastos': 21000},
    ]
    
    return JsonResponse({'ventas': data})
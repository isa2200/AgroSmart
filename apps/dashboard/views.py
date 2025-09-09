from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from apps.aves.models import LoteAves, ProduccionHuevos, AlertaSanitaria
from apps.usuarios.decorators import role_required


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def dashboard_principal(request):
    """
    Vista principal del dashboard con métricas generales
    """
    # Métricas generales
    total_aves = LoteAves.objects.filter(estado='activo').count()
    
    # Producción del mes actual
    mes_actual = timezone.now().replace(day=1)
    
    produccion_aves = ProduccionHuevos.objects.filter(
        fecha__gte=mes_actual
    ).aggregate(
        total_yumbos=Sum('yumbos'),
        total_extra=Sum('extra'),
        total_aa=Sum('aa'),
        total_a=Sum('a'),
        total_b=Sum('b'),
        total_c=Sum('c')
    )
    
    # Calcular el total sumando todos los tipos
    total_produccion = (
        (produccion_aves['total_yumbos'] or 0) +
        (produccion_aves['total_extra'] or 0) +
        (produccion_aves['total_aa'] or 0) +
        (produccion_aves['total_a'] or 0) +
        (produccion_aves['total_b'] or 0) +
        (produccion_aves['total_c'] or 0)
    )
    
    
    # Alertas activas
    # Alertas sanitarias activas (usar AlertaSanitaria de aves)
    alertas = AlertaSanitaria.objects.filter(
        fecha_deteccion__gte=timezone.now().date() - timedelta(days=7),
        resuelta=False
    ).select_related('lote')[:5]
    
    context = {
        'total_aves': total_aves,
        'produccion_aves': total_produccion,
        'alertas': alertas,
    }
    
    return render(request, 'dashboard/principal.html', context)

@login_required
def datos_graficos_produccion(request):
    """
    Proporciona datos para gráficos de producción diaria.
    """
    # Obtener los últimos 30 días de producción
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    
    # Calcular producción diaria
    produccion_diaria = []
    for i in range(30):
        fecha = fecha_inicio + timedelta(days=i)
        
        # Corregir la agregación de campos
        produccion_dia = ProduccionHuevos.objects.filter(
            fecha=fecha
        ).aggregate(
            total_yumbos=Sum('yumbos'),
            total_extra=Sum('extra'),
            total_aa=Sum('aa'),
            total_a=Sum('a'),
            total_b=Sum('b'),
            total_c=Sum('c')
        )
        
        # Calcular total de huevos del día
        total_huevos = sum([
            produccion_dia['total_yumbos'] or 0,
            produccion_dia['total_extra'] or 0,
            produccion_dia['total_aa'] or 0,
            produccion_dia['total_a'] or 0,
            produccion_dia['total_b'] or 0,
            produccion_dia['total_c'] or 0
        ])
        
        produccion_diaria.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'total': total_huevos,
            'detalle': produccion_dia
        })
    
    return JsonResponse({
        'produccion_diaria': produccion_diaria
    })

@login_required
def datos_inventario_animales(request):
    """
    Proporciona datos del inventario actual de animales.
    """
    # Obtener lotes activos con sus cantidades
    lotes_activos = LoteAves.objects.filter(
        estado='activo'
    ).values('linea').annotate(
        total_aves=Sum('cantidad_actual')
    ).order_by('linea')
    
    # Preparar datos para el gráfico
    datos_inventario = []
    for lote in lotes_activos:
        datos_inventario.append({
            'linea': lote['linea'],
            'cantidad': lote['total_aves'] or 0
        })
    
    return JsonResponse({
        'inventario_animales': datos_inventario
    })
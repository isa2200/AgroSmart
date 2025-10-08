from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
from apps.aves.models import LoteAves, BitacoraDiaria
from apps.dashboard.models import AlertaSistema  # Usar el AlertaSistema del dashboard
from apps.usuarios.decorators import role_required

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario', 'solo_vista'])
def dashboard_principal(request):
    """
    Vista principal del dashboard con métricas generales
    """
    # Métricas generales
    total_aves = LoteAves.objects.filter(estado='activo').count()
    
    # Producción del mes actual usando BitacoraDiaria
    mes_actual = timezone.now().replace(day=1)
    
    produccion_aves = BitacoraDiaria.objects.filter(
        fecha__gte=mes_actual
    ).aggregate(
        total_huevos=Sum(
            F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + 
            F('produccion_b') + F('produccion_c')
        )
    )
    
    total_produccion = produccion_aves['total_huevos'] or 0
    
    # Alertas activas usando AlertaSistema del dashboard
    alertas = AlertaSistema.objects.filter(
        created_at__gte=timezone.now().date() - timedelta(days=7),
        leida=False
    )[:5]
    
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
    
    # Calcular producción diaria usando BitacoraDiaria
    produccion_diaria = []
    for i in range(30):
        fecha = fecha_inicio + timedelta(days=i)
        
        produccion_dia = BitacoraDiaria.objects.filter(
            fecha=fecha
        ).aggregate(
            total_huevos=Sum('huevos_recolectados')
        )
        
        total_huevos = produccion_dia['total_huevos'] or 0
        
        produccion_diaria.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'total': total_huevos
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
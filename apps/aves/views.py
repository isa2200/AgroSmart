"""
Vistas para el módulo avícola.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from datetime import timedelta
import json

from apps.usuarios.decorators import role_required, acceso_modulo_aves_required, puede_editar_required, puede_eliminar_required, veterinario_required
from .models import *
from .forms import *
from .utils import generar_alertas, actualizar_inventario_huevos, exportar_reporte_pdf


@login_required
@acceso_modulo_aves_required
def dashboard_aves(request):
    """Dashboard principal del módulo avícola mejorado."""
    from django.db.models import F
    
    hoy = timezone.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    hace_30_dias = hoy - timedelta(days=30)
    fecha_30d_atras = hace_30_dias
    
    # Filtros opcionales
    galpon_filtro = request.GET.get('galpon')
    lote_filtro = request.GET.get('lote')
    
    # Query base para lotes activos
    lotes_query = LoteAves.objects.filter(is_active=True)
    if galpon_filtro:
        lotes_query = lotes_query.filter(galpon__icontains=galpon_filtro)
    if lote_filtro:
        lotes_query = lotes_query.filter(id=lote_filtro)
    
    # Estadísticas generales
    total_lotes = lotes_query.count()
    total_aves = lotes_query.aggregate(total=Sum('numero_aves_actual'))['total'] or 0
    
    # Separar lotes por tipo (ponedoras vs engorde)
    lotes_ponedoras = lotes_query.filter(estado='postura')
    lotes_engorde = lotes_query.filter(estado='levante')
    
    # INDICADORES PONEDORAS
    # Producción de huevos - AGREGADO: Consultas para 7 días
    bitacoras_ponedoras_hoy = BitacoraDiaria.objects.filter(
        lote__in=lotes_ponedoras, fecha=hoy
    )
    bitacoras_ponedoras_7d = BitacoraDiaria.objects.filter(
        lote__in=lotes_ponedoras, fecha__gte=hace_7_dias, fecha__lte=hoy
    )
    bitacoras_ponedoras_30d = BitacoraDiaria.objects.filter(
        lote__in=lotes_ponedoras, fecha__gte=hace_30_dias, fecha__lte=hoy
    )
    
    # Producción diaria, semanal y mensual - CORREGIDO
    produccion_hoy = bitacoras_ponedoras_hoy.aggregate(
        total=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + 
                    F('produccion_b') + F('produccion_c'))
    )['total'] or 0
    
    # AGREGADO: Producción de 7 días
    produccion_7d = bitacoras_ponedoras_7d.aggregate(
        total=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + 
                    F('produccion_b') + F('produccion_c'))
    )['total'] or 0
    
    produccion_30d = bitacoras_ponedoras_30d.aggregate(
        total=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + 
                    F('produccion_b') + F('produccion_c'))
    )['total'] or 0
    
    # Porcentaje de postura
    aves_ponedoras = lotes_ponedoras.aggregate(total=Sum('numero_aves_actual'))['total'] or 0
    porcentaje_postura_hoy = (produccion_hoy / aves_ponedoras * 100) if aves_ponedoras > 0 else 0
    # AGREGADO: Porcentaje de postura 7 días
    porcentaje_postura_7d = (produccion_7d / (aves_ponedoras * 7) * 100) if aves_ponedoras > 0 else 0
    porcentaje_postura_30d = (produccion_30d / (aves_ponedoras * 30) * 100) if aves_ponedoras > 0 else 0
    
    # Producción ideal vs real (asumiendo 85% como ideal)
    produccion_ideal_hoy = aves_ponedoras * 0.85
    # AGREGADO: Producción ideal 7 días
    produccion_ideal_7d = aves_ponedoras * 0.85 * 7
    produccion_ideal_30d = aves_ponedoras * 0.85 * 30
    diferencia_ideal_hoy = produccion_hoy - produccion_ideal_hoy
    # AGREGADO: Diferencia ideal 7 días
    diferencia_ideal_7d = produccion_7d - produccion_ideal_7d
    diferencia_ideal_30d = produccion_30d - produccion_ideal_30d
    
    # INDICADORES ENGORDE
    # Peso promedio y consumo - AGREGADO: Consultas para 7 días
    bitacoras_engorde_hoy = BitacoraDiaria.objects.filter(
        lote__in=lotes_engorde, fecha=hoy
    )
    bitacoras_engorde_7d = BitacoraDiaria.objects.filter(
        lote__in=lotes_engorde, fecha__gte=hace_7_dias, fecha__lte=hoy
    )
    bitacoras_engorde_30d = BitacoraDiaria.objects.filter(
        lote__in=lotes_engorde, fecha__gte=hace_30_dias, fecha__lte=hoy
    )
    
    # Consumo de alimento
    consumo_total_hoy = bitacoras_engorde_hoy.aggregate(total=Sum('consumo_concentrado'))['total'] or 0
    # AGREGADO: Consumo total 7 días
    consumo_total_7d = bitacoras_engorde_7d.aggregate(total=Sum('consumo_concentrado'))['total'] or 0
    consumo_total_30d = bitacoras_engorde_30d.aggregate(total=Sum('consumo_concentrado'))['total'] or 0
    aves_engorde = lotes_engorde.aggregate(total=Sum('numero_aves_actual'))['total'] or 0
    consumo_por_ave_hoy = (consumo_total_hoy / aves_engorde) if aves_engorde > 0 else 0
    # AGREGADO: Consumo promedio 7 días
    consumo_promedio_7d = (consumo_total_7d / (aves_engorde * 7)) if aves_engorde > 0 else 0
    consumo_promedio_30d = (consumo_total_30d / (aves_engorde * 30)) if aves_engorde > 0 else 0
    
    # ... existing code ...
    
    # MORTALIDAD - CORREGIDO
    mortalidad_hoy = BitacoraDiaria.objects.filter(
        fecha=hoy, lote__in=lotes_query
    ).aggregate(total=Sum('mortalidad'))['total'] or 0
    
    mortalidad_30d = BitacoraDiaria.objects.filter(
        fecha__gte=hace_30_dias, fecha__lte=hoy, lote__in=lotes_query
    ).aggregate(total=Sum('mortalidad'))['total'] or 0
    
    porcentaje_mortalidad_hoy = (mortalidad_hoy / total_aves * 100) if total_aves > 0 else 0
    porcentaje_mortalidad_30d = (mortalidad_30d / total_aves * 100) if total_aves > 0 else 0
    
    # GRÁFICOS DE TENDENCIA - CAMBIADO A MENSUAL (30 DÍAS)
    # Evolución producción últimos 30 días
    evolucion_produccion = []
    for i in range(30):
        fecha = hoy - timedelta(days=29-i)
        prod_dia = BitacoraDiaria.objects.filter(
            fecha=fecha, lote__in=lotes_ponedoras
        ).aggregate(
            total=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + 
                     F('produccion_b') + F('produccion_c'))
        )['total'] or 0
        evolucion_produccion.append({
            'fecha': fecha.strftime('%d/%m'),
            'produccion': prod_dia,
            'porcentaje': (prod_dia / aves_ponedoras * 100) if aves_ponedoras > 0 else 0
        })
    
    # Evolución mortalidad últimos 30 días
    evolucion_mortalidad = []
    for i in range(30):
        fecha = hoy - timedelta(days=29-i)
        mort_dia = BitacoraDiaria.objects.filter(
            fecha=fecha, lote__in=lotes_query
        ).aggregate(total=Sum('mortalidad'))['total'] or 0
        evolucion_mortalidad.append({
            'fecha': fecha.strftime('%d/%m'),
            'mortalidad': mort_dia
        })
    
    # COMPARACIÓN ENTRE GALPONES - CAMBIADO A MENSUAL
    comparacion_galpones = []
    galpones = lotes_query.values_list('galpon', flat=True).distinct()
    for galpon in galpones:
        lotes_galpon = lotes_query.filter(galpon=galpon)
        aves_galpon = lotes_galpon.aggregate(total=Sum('numero_aves_actual'))['total'] or 0
        
        # Producción del galpón (últimos 30 días)
        prod_galpon = BitacoraDiaria.objects.filter(
            lote__in=lotes_galpon, fecha__gte=hace_30_dias, fecha__lte=hoy
        ).aggregate(
            total=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + 
                     F('produccion_b') + F('produccion_c'))
        )['total'] or 0
        
        # Mortalidad del galpón (últimos 30 días)
        mort_galpon = BitacoraDiaria.objects.filter(
            lote__in=lotes_galpon, fecha__gte=hace_30_dias, fecha__lte=hoy
        ).aggregate(total=Sum('mortalidad'))['total'] or 0
        
        comparacion_galpones.append({
            'galpon': galpon,
            'aves': aves_galpon,
            'produccion_30d': prod_galpon,
            'mortalidad_30d': mort_galpon,
            'porcentaje_postura': (prod_galpon / (aves_galpon * 30) * 100) if aves_galpon > 0 else 0,
            'porcentaje_mortalidad': (mort_galpon / aves_galpon * 100) if aves_galpon > 0 else 0
        })
    
    # ALERTAS Y NOTIFICACIONES
    alertas_activas = AlertaSistema.objects.filter(leida=False).count()
    alertas_criticas_count = AlertaSistema.objects.filter(leida=False, nivel='critica').count()
    
    # Generar alertas automáticas
    alertas_criticas = []
    
    # Alerta baja postura
    if porcentaje_postura_hoy < 70:
        nivel = 'critica' if porcentaje_postura_hoy < 50 else 'normal'
        alertas_criticas.append({
            'tipo': 'danger' if nivel == 'critica' else 'warning',
            'mensaje': f'Postura {"crítica" if nivel == "critica" else "baja"}: {porcentaje_postura_hoy:.1f}% (objetivo: 85%)',
            'icono': 'fas fa-egg'
        })
    
    # Alerta mortalidad alta
    if porcentaje_mortalidad_hoy > 2:
        nivel = 'critica' if porcentaje_mortalidad_hoy > 5 else 'normal'
        alertas_criticas.append({
            'tipo': 'danger' if nivel == 'critica' else 'warning',
            'mensaje': f'Mortalidad {"crítica" if nivel == "critica" else "elevada"}: {porcentaje_mortalidad_hoy:.1f}% hoy',
            'icono': 'fas fa-skull-crossbones'
        })
    
    # Alerta consumo anormal
    if consumo_por_ave_hoy > 0.15 or (consumo_por_ave_hoy < 0.08 and consumo_por_ave_hoy > 0):
        alertas_criticas.append({
            'tipo': 'warning',  # Consumo anormal siempre es normal, no crítico
            'mensaje': f'Consumo anormal: {consumo_por_ave_hoy*1000:.0f}g por ave',
            'icono': 'fas fa-utensils'
        })
    
    # Vacunas pendientes
    vacunas_pendientes = PlanVacunacion.objects.filter(
        aplicada=False,
        fecha_programada__lte=timezone.now().date() + timedelta(days=3)
    ).count()
    
    # Inventario de huevos
    inventario_huevos = []
    for categoria in ['AAA', 'AA', 'A', 'B', 'C']:
        inventario, created = InventarioHuevos.objects.get_or_create(
            categoria=categoria,
            defaults={'cantidad_actual': 0, 'cantidad_minima': 100}
        )
        inventario_huevos.append(inventario)
    
    # Top 5 lotes por rendimiento (30 días)
    top_lotes = []
    for lote in lotes_query[:5]:  # Cambiar lotes_activos por lotes_query
        produccion_30d = BitacoraDiaria.objects.filter(
            lote=lote,
            fecha__gte=fecha_30d_atras
        ).aggregate(total=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')))['total'] or 0
        
        porcentaje_postura = (produccion_30d / (lote.numero_aves_actual * 30) * 100) if lote.numero_aves_actual > 0 else 0
        
        top_lotes.append({
            'lote': lote,
            'edad_dias': lote.edad_dias,
            'porcentaje_postura': porcentaje_postura,
            'produccion_30d': produccion_30d
        })
    
    # Ordenar por porcentaje de postura
    top_lotes.sort(key=lambda x: x['porcentaje_postura'], reverse=True)
    
    context = {
        # Estadísticas generales
        'total_lotes': total_lotes,
        'total_aves': total_aves,
        'aves_ponedoras': aves_ponedoras,
        'aves_engorde': aves_engorde,
        
        # Indicadores ponedoras
        'produccion_hoy': produccion_hoy,
        'produccion_7d': produccion_7d,  # AGREGADO
        'produccion_30d': produccion_30d,
        'porcentaje_postura_hoy': round(porcentaje_postura_hoy, 1),
        'porcentaje_postura_7d': round(porcentaje_postura_7d, 1),  # AGREGADO
        'porcentaje_postura_30d': round(porcentaje_postura_30d, 1),
        'produccion_ideal_hoy': round(produccion_ideal_hoy),
        'diferencia_ideal_hoy': round(diferencia_ideal_hoy),
        'diferencia_ideal_7d': round(diferencia_ideal_7d),  # AGREGADO
        'diferencia_ideal_30d': round(diferencia_ideal_30d),
        
        # Indicadores engorde
        'consumo_total_hoy': round(consumo_total_hoy, 1),
        'consumo_por_ave_hoy': round(consumo_por_ave_hoy * 1000),  # En gramos
        'consumo_promedio_7d': round(consumo_promedio_7d * 1000),  # AGREGADO - En gramos
        'consumo_promedio_30d': round(consumo_promedio_30d * 1000),  # En gramos
        
        # Mortalidad
        'mortalidad_hoy': mortalidad_hoy,
        'mortalidad_30d': mortalidad_30d,
        'porcentaje_mortalidad_hoy': round(porcentaje_mortalidad_hoy, 2),
        'porcentaje_mortalidad_30d': round(porcentaje_mortalidad_30d, 2),
        
        # Gráficos
        'evolucion_produccion': evolucion_produccion,
        'evolucion_mortalidad': evolucion_mortalidad,
        'comparacion_galpones': comparacion_galpones,
        
        # Alertas
        'alertas_pendientes': alertas_activas,
        'alertas_criticas': alertas_criticas,
        'vacunas_pendientes': vacunas_pendientes,
        
        # Otros datos
        'inventario_huevos': inventario_huevos,
        'top_lotes': top_lotes[:5],
        
        # Para filtros
        'galpones_disponibles': list(galpones),
        'lotes_disponibles': lotes_query.values('id', 'codigo'),
        'galpon_filtro': galpon_filtro,
        'lote_filtro': lote_filtro,
        
        # JSON para gráficos
        'evolucion_produccion_json': json.dumps(evolucion_produccion),
        'evolucion_mortalidad_json': json.dumps(evolucion_mortalidad),
        'comparacion_galpones_json': json.dumps(comparacion_galpones),
    }
    
    return render(request, 'aves/dashboard.html', context)


@login_required
@acceso_modulo_aves_required
@puede_editar_required
def bitacora_diaria_create(request):
    """Crear nueva bitácora diaria."""
    if request.method == 'POST':
        form = BitacoraDiariaForm(request.POST)
        if form.is_valid():
            bitacora = form.save(commit=False)
            bitacora.usuario_registro = request.user
            bitacora.save()
            
            # Actualizar inventario de huevos
            actualizar_inventario_huevos(bitacora)
            
            # Generar alertas automáticas
            generar_alertas(bitacora)
            
            messages.success(request, 'Bitácora diaria registrada exitosamente.')
            return redirect('aves:bitacora_list')
        else:
            messages.error(request, 'Error al registrar la bitácora. Verifique los datos.')
    else:
        form = BitacoraDiariaForm()
    
    return render(request, 'aves/bitacora_form.html', {'form': form})


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def bitacora_list(request):
    """Lista de bitácoras diarias."""
    bitacoras = BitacoraDiaria.objects.select_related('lote', 'usuario_registro').all()
    
    # Filtros
    lote_id = request.GET.get('lote')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if lote_id:
        bitacoras = bitacoras.filter(lote_id=lote_id)
    if fecha_desde:
        bitacoras = bitacoras.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        bitacoras = bitacoras.filter(fecha__lte=fecha_hasta)
    
    paginator = Paginator(bitacoras, 20)
    page = request.GET.get('page')
    bitacoras = paginator.get_page(page)
    
    lotes = LoteAves.objects.filter(is_active=True)
    
    context = {
        'bitacoras': bitacoras,
        'lotes': lotes,
        'filtros': {
            'lote': lote_id,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    
    return render(request, 'aves/bitacora_list.html', context)


@login_required
@acceso_modulo_aves_required
@puede_editar_required
def lote_create(request):
    """Crear nuevo lote de aves."""
    if request.method == 'POST':
        form = LoteAvesForm(request.POST)
        if form.is_valid():
            try:
                lote = form.save(commit=False)
                lote.numero_aves_actual = lote.numero_aves_inicial
                lote.save()
                messages.success(request, f'Lote {lote.codigo} creado exitosamente.')
                return redirect('aves:lote_detail', pk=lote.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar el lote: {str(e)}')
        else:
            # Mostrar errores específicos para debugging
            messages.error(request, 'Error al validar el formulario:')
            for field, errors in form.errors.items():
                field_name = form.fields[field].label if field in form.fields else field
                for error in errors:
                    messages.error(request, f'• {field_name}: {error}')
            
            # Errores no específicos de campo
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, f'• {error}')
    else:
        form = LoteAvesForm()
    
    return render(request, 'aves/lote_form.html', {'form': form})

@login_required
@acceso_modulo_aves_required
@puede_editar_required
def lote_edit(request, pk):
    """Editar lote de aves con justificación obligatoria."""
    lote = get_object_or_404(LoteAves, pk=pk)
    
    if request.method == 'POST':
        form = LoteAvesEditForm(request.POST, instance=lote)
        
        if form.is_valid():
            # Verificar si realmente hay cambios
            changed_data = [field for field in form.changed_data if field != 'justificacion']
            
            if not changed_data:
                messages.info(request, 'No se detectaron cambios en el lote.')
                return redirect('aves:lote_detail', pk=lote.pk)
            
            # Registrar modificación antes de guardar
            valores_anteriores = {}
            valores_nuevos = {}
            
            for field in changed_data:
                valores_anteriores[field] = str(getattr(lote, field))
                valores_nuevos[field] = str(form.cleaned_data[field])
            
            lote_actualizado = form.save()
            
            # Crear registro de modificación
            RegistroModificacion.objects.create(
                usuario=request.user,
                modelo='LoteAves',
                objeto_id=lote.pk,
                accion='UPDATE',
                campos_modificados=changed_data,
                valores_anteriores=valores_anteriores,
                valores_nuevos=valores_nuevos,
                justificacion=form.cleaned_data['justificacion']
            )
            
            messages.success(request, f'Lote {lote.codigo} actualizado exitosamente.')
            return redirect('aves:lote_detail', pk=lote.pk)
        else:
            messages.error(request, 'Error al validar el formulario. Revise los campos marcados.')
    else:
        form = LoteAvesEditForm(instance=lote)
    
    context = {
        'form': form,
        'lote': lote,
        'titulo': f'Editar Lote {lote.codigo}',
    }
    
    return render(request, 'aves/lote_edit.html', context)

@login_required
@acceso_modulo_aves_required
@puede_eliminar_required
@require_http_methods(["POST"])
def lote_delete(request, pk):
    """Eliminar lote y sus bitácoras asociadas con justificación obligatoria."""
    lote = get_object_or_404(LoteAves, pk=pk)
    
    justificacion = request.POST.get('justificacion', '').strip()
    
    if not justificacion or len(justificacion) < 10:
        messages.error(request, 'La justificación para eliminar el lote es obligatoria y debe tener al menos 10 caracteres.')
        return redirect('aves:lote_list')
    
    try:
        # Contar bitácoras que se eliminarán para informar al usuario
        bitacoras_count = BitacoraDiaria.objects.filter(lote=lote).count()
        
        # Registrar la eliminación antes de eliminar
        RegistroModificacion.objects.create(
            usuario=request.user,
            modelo='LoteAves',
            objeto_id=lote.pk,
            accion='DELETE',
            campos_modificados=['eliminado_fisicamente'],
            valores_anteriores={
                'is_active': 'True', 
                'codigo': lote.codigo,
                'bitacoras_asociadas': bitacoras_count
            },
            valores_nuevos={'eliminado_fisicamente': 'True'},
            justificacion=justificacion
        )
        
        # Eliminar físicamente el lote (esto eliminará automáticamente las bitácoras por CASCADE)
        codigo_lote = lote.codigo
        lote.delete()
        
        if bitacoras_count > 0:
            messages.success(request, 
                f'Lote {codigo_lote} eliminado exitosamente junto con {bitacoras_count} bitácora(s) asociada(s).')
        else:
            messages.success(request, f'Lote {codigo_lote} eliminado exitosamente.')
            
    except Exception as e:
        messages.error(request, f'Error al eliminar el lote: {str(e)}')
    
    return redirect('aves:lote_list')

@login_required
@acceso_modulo_aves_required
def lote_list(request):
    """Lista de lotes de aves."""
    lotes = LoteAves.objects.filter(is_active=True).order_by('-fecha_llegada')
    
    # Filtros
    estado_filtro = request.GET.get('estado')
    galpon_filtro = request.GET.get('galpon')
    linea_genetica_filtro = request.GET.get('linea_genetica')
    
    if estado_filtro:
        lotes = lotes.filter(estado=estado_filtro)
    if galpon_filtro:
        lotes = lotes.filter(galpon__icontains=galpon_filtro)
    if linea_genetica_filtro:
        lotes = lotes.filter(linea_genetica=linea_genetica_filtro)
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(lotes, 20)
    page = request.GET.get('page')
    lotes = paginator.get_page(page)
    
    context = {
        'lotes': lotes,
        'estados': LoteAves.ESTADOS,
        'lineas_geneticas': LoteAves.LINEAS_GENETICAS,
        'filtros': {
            'estado': estado_filtro,
            'galpon': galpon_filtro,
            'linea_genetica': linea_genetica_filtro,
        }
    }
    
    return render(request, 'aves/lote_list.html', context)


@login_required
@acceso_modulo_aves_required
def lote_detail(request, pk):
    """Detalle de un lote."""
    lote = get_object_or_404(LoteAves, pk=pk)
    
    # Estadísticas del lote
    bitacoras = BitacoraDiaria.objects.filter(lote=lote).order_by('-fecha')[:30]
    
    # Producción total
    produccion_total = bitacoras.aggregate(
        total=Sum('produccion_aaa') + Sum('produccion_aa') + Sum('produccion_a') + 
              Sum('produccion_b') + Sum('produccion_c'))['total'] or 0
    
    # Mortalidad total
    mortalidad_total = bitacoras.aggregate(total=Sum('mortalidad'))['total'] or 0
    
    # Consumo promedio
    consumo_promedio = bitacoras.aggregate(promedio=Avg('consumo_concentrado'))['promedio'] or 0
    
    context = {
        'lote': lote,
        'bitacoras': bitacoras[:10],  # Últimas 10 bitácoras
        'produccion_total': produccion_total,
        'mortalidad_total': mortalidad_total,
        'consumo_promedio': round(consumo_promedio, 2),
    }
    
    return render(request, 'aves/lote_detail.html', context)


@login_required
@acceso_modulo_aves_required
def inventario_huevos(request):
    """Vista de inventario de huevos."""
    from django.db.models import Sum
    
    inventarios = InventarioHuevos.objects.all()
    
    # Calcular total de gallinas para mostrar en el contexto
    total_gallinas = LoteAves.objects.filter(
        is_active=True,
        estado='postura'
    ).aggregate(total=Sum('numero_aves_actual'))['total'] or 0
    
    # Movimientos recientes - obtener detalles en lugar de movimientos principales
    movimientos_recientes = DetalleMovimientoHuevos.objects.select_related(
        'movimiento__usuario_registro', 'movimiento'
    ).order_by('-movimiento__fecha')[:20]
    
    # Estadísticas de stock automático
    inventarios_automaticos = inventarios.filter(stock_automatico=True).count()
    inventarios_manuales = inventarios.filter(stock_automatico=False).count()
    
    context = {
        'inventarios': inventarios,
        'movimientos_recientes': movimientos_recientes,
        'total_gallinas': total_gallinas,
        'inventarios_automaticos': inventarios_automaticos,
        'inventarios_manuales': inventarios_manuales,
    }
    
    return render(request, 'aves/inventario_huevos.html', context)


@login_required
@role_required(['superusuario', 'admin_aves'])
def movimiento_huevos_create(request):
    """Crear movimiento de huevos con múltiples detalles."""
    from django.forms import formset_factory
    from django.db import transaction
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    
    DetalleMovimientoHuevosFormSet = formset_factory(
        DetalleMovimientoHuevosForm,
        extra=1,
        min_num=1,
        validate_min=True,
        can_delete=True
    )
    
    if request.method == 'POST':
        logger.info(f"POST data received: {request.POST}")
        
        form = MovimientoHuevosForm(request.POST)
        formset = DetalleMovimientoHuevosFormSet(request.POST)
        
        logger.info(f"Form valid: {form.is_valid()}")
        logger.info(f"Formset valid: {formset.is_valid()}")
        
        # Validar formulario principal
        if not form.is_valid():
            logger.error(f"Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
        
        # Validar formset
        if not formset.is_valid():
            logger.error(f"Formset errors: {formset.errors}")
            logger.error(f"Formset non_form_errors: {formset.non_form_errors()}")
            
            # Mostrar errores específicos de cada formulario
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    logger.error(f"Form {i} errors: {form_errors}")
                    for field, errors in form_errors.items():
                        for error in errors:
                            messages.error(request, f'Error en detalle {i+1}, campo {field}: {error}')
            
            # Mostrar errores no relacionados con campos específicos
            for error in formset.non_form_errors():
                messages.error(request, f'Error en detalles: {error}')
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Guardar el movimiento principal
                    movimiento = form.save(commit=False)
                    movimiento.usuario_registro = request.user
                    movimiento.save()
                    logger.info(f"Movimiento guardado con ID: {movimiento.id}")
                    
                    # Contar detalles válidos
                    detalles_guardados = 0
                    errores_stock = []
                    
                    # Guardar los detalles y actualizar inventario
                    for i, detalle_form in enumerate(formset):
                        if detalle_form.cleaned_data and not detalle_form.cleaned_data.get('DELETE', False):
                            logger.info(f"Procesando detalle {i}: {detalle_form.cleaned_data}")
                            
                            try:
                                detalle = detalle_form.save(commit=False)
                                detalle.movimiento = movimiento
                                
                                # Validar stock antes de guardar
                                if movimiento.tipo_movimiento in ['venta', 'autoconsumo', 'baja']:
                                    try:
                                        inventario = InventarioHuevos.objects.get(categoria=detalle.categoria_huevo)
                                        if detalle.cantidad > inventario.cantidad_actual:
                                            errores_stock.append(
                                                f'Detalle {i+1}: No hay suficiente stock de huevos {detalle.categoria_huevo}. '
                                                f'Disponible: {inventario.cantidad_actual}, Solicitado: {detalle.cantidad}'
                                            )
                                            continue
                                    except InventarioHuevos.DoesNotExist:
                                        errores_stock.append(
                                            f'Detalle {i+1}: No existe inventario para la categoría {detalle.categoria_huevo}'
                                        )
                                        continue
                                
                                # Guardar el detalle
                                detalle.save()
                                detalles_guardados += 1
                                logger.info(f"Detalle {i} guardado con ID: {detalle.id}")
                                
                                # Actualizar inventario
                                try:
                                    inventario, created = InventarioHuevos.objects.get_or_create(
                                        categoria=detalle.categoria_huevo,
                                        defaults={
                                            'cantidad_actual': 0,
                                            'cantidad_minima': 100
                                        }
                                    )
                                    
                                    if created:
                                        logger.info(f"Inventario creado para categoría {detalle.categoria_huevo}")
                                    
                                    cantidad_anterior = inventario.cantidad_actual
                                    
                                    if movimiento.tipo_movimiento in ['venta', 'autoconsumo', 'baja']:
                                        inventario.cantidad_actual -= detalle.cantidad
                                    else:  # devolución
                                        inventario.cantidad_actual += detalle.cantidad
                                    
                                    inventario.save()
                                    logger.info(f"Inventario actualizado para {detalle.categoria_huevo}: {cantidad_anterior} -> {inventario.cantidad_actual}")
                                    
                                except Exception as e:
                                    logger.error(f"Error actualizando inventario: {str(e)}")
                                    raise ValidationError(f"Error actualizando inventario: {str(e)}")
                                    
                            except ValidationError as e:
                                logger.error(f"ValidationError en detalle {i}: {str(e)}")
                                errores_stock.append(f'Detalle {i+1}: {str(e)}')
                                continue
                    
                    # Verificar si hubo errores de stock
                    if errores_stock:
                        for error in errores_stock:
                            messages.error(request, error)
                        raise ValidationError("Errores de validación de stock")
                    
                    if detalles_guardados == 0:
                        raise ValidationError("Debe agregar al menos un detalle válido al movimiento.")
                    
                    logger.info(f"Movimiento completado. Detalles guardados: {detalles_guardados}")
                
                messages.success(request, f'Movimiento de huevos registrado exitosamente con {detalles_guardados} detalles.')
                return redirect('aves:inventario_huevos')
                
            except ValidationError as e:
                logger.error(f"ValidationError: {str(e)}")
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            messages.error(request, f'Error en {field}: {error}')
                else:
                    messages.error(request, str(e))
            except Exception as e:
                logger.error(f"Error inesperado: {str(e)}")
                messages.error(request, f'Error al registrar el movimiento: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores indicados en el formulario.')
    else:
        form = MovimientoHuevosForm()
        formset = DetalleMovimientoHuevosFormSet()
    
    # Obtener inventarios para mostrar stock disponible
    try:
        inventarios = InventarioHuevos.objects.all()
        inventarios_dict = {inv.categoria: inv.cantidad_actual for inv in inventarios}
    except Exception as e:
        logger.error(f"Error obteniendo inventarios: {str(e)}")
        inventarios_dict = {}
        messages.warning(request, 'No se pudo cargar la información de inventarios.')
    
    context = {
        'form': form,
        'formset': formset,
        'inventarios': inventarios_dict,
        'inventario_json': json.dumps(inventarios_dict),
        'title': 'Nuevo Movimiento de Huevos',
    }
    
    return render(request, 'aves/movimiento_huevos_form.html', context)


@login_required
@veterinario_required
def plan_vacunacion_list(request):
    """Lista de planes de vacunación."""
    planes = PlanVacunacion.objects.select_related('lote', 'tipo_vacuna', 'veterinario').all()
    
    # Filtros
    lote_id = request.GET.get('lote')
    aplicada = request.GET.get('aplicada')
    
    if lote_id:
        planes = planes.filter(lote_id=lote_id)
    if aplicada == 'true':
        planes = planes.filter(aplicada=True)
    elif aplicada == 'false':
        planes = planes.filter(aplicada=False)
    
    paginator = Paginator(planes, 20)
    page = request.GET.get('page')
    planes = paginator.get_page(page)
    
    lotes = LoteAves.objects.filter(is_active=True)
    
    context = {
        'planes': planes,
        'lotes': lotes,
        'filtros': {
            'lote': lote_id,
            'aplicada': aplicada,
        }
    }
    
    return render(request, 'aves/plan_vacunacion_list.html', context)


@login_required
@veterinario_required
def plan_vacunacion_create(request):
    """Crear plan de vacunación."""
    if request.method == 'POST':
        form = PlanVacunacionForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.veterinario = request.user
            plan.save()
            messages.success(request, 'Plan de vacunación creado exitosamente.')
            return redirect('aves:plan_vacunacion_list')
        else:
            messages.error(request, 'Error al crear el plan de vacunación.')
    else:
        form = PlanVacunacionForm()
    
    # Obtener todas las vacunas para el JavaScript
    vacunas = TipoVacuna.objects.all()
    vacunas_data = {}
    for vacuna in vacunas:
        vacunas_data[vacuna.id] = {
            'nombre': vacuna.nombre,
            'laboratorio': vacuna.laboratorio,
            'dosis_por_ave': str(vacuna.dosis_por_ave),
            'via_aplicacion': vacuna.via_aplicacion,
            'enfermedad_previene': vacuna.enfermedad_previene,
            'intervalo_dias': vacuna.intervalo_dias
        }
    
    context = {
        'form': form,
        'vacunas_data': json.dumps(vacunas_data)
    }
    
    return render(request, 'aves/plan_vacunacion_form.html', context)


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def alertas_list(request):
    """Lista de alertas del sistema."""
    alertas = AlertaSistema.objects.select_related('lote', 'usuario_destinatario').order_by('-fecha_generacion')
    
    # Filtros corregidos para coincidir con el modelo real
    tipo_alerta = request.GET.get('tipo')
    nivel = request.GET.get('nivel')
    prioridad = request.GET.get('prioridad')  # Mapear prioridad a nivel
    estado = request.GET.get('estado')
    lote_id = request.GET.get('lote')
    leida = request.GET.get('leida')
    
    # Aplicar filtros
    if tipo_alerta:
        alertas = alertas.filter(tipo_alerta=tipo_alerta)
    
    if nivel:
        alertas = alertas.filter(nivel=nivel)
    
    # Mapear prioridad del template a nivel del modelo
    if prioridad:
        if prioridad == 'critica':
            alertas = alertas.filter(nivel='critica')
        elif prioridad in ['alta', 'media', 'baja']:
            alertas = alertas.filter(nivel='normal')
    
    # Filtrar por estado
    if estado:
        if estado == 'activa':
            alertas = alertas.filter(is_active=True, leida=False)
        elif estado == 'leida':
            alertas = alertas.filter(leida=True)
        elif estado == 'resuelta':
            alertas = alertas.filter(is_active=False)
    
    if lote_id:
        alertas = alertas.filter(lote_id=lote_id)
    
    if leida == 'true':
        alertas = alertas.filter(leida=True)
    elif leida == 'false':
        alertas = alertas.filter(leida=False)
    
    # Estadísticas corregidas para coincidir con el template
    stats = {
        'criticas': AlertaSistema.objects.filter(is_active=True, leida=False, nivel='critica').count(),
        'altas': AlertaSistema.objects.filter(is_active=True, leida=False, nivel='normal').count() // 3,  # Dividir normales en 3 categorías ficticias
        'medias': AlertaSistema.objects.filter(is_active=True, leida=False, nivel='normal').count() // 3,
        'bajas': AlertaSistema.objects.filter(is_active=True, leida=False, nivel='normal').count() // 3,
        'total_no_leidas': AlertaSistema.objects.filter(is_active=True, leida=False).count(),
        'total': AlertaSistema.objects.filter(is_active=True).count(),
    }
    
    # Obtener lotes para filtros - corregido
    lotes = LoteAves.objects.filter(is_active=True)
    
    paginator = Paginator(alertas, 20)
    page = request.GET.get('page')
    alertas_paginadas = paginator.get_page(page)
    
    context = {
        'alertas': alertas_paginadas,
        'tipos_alerta': AlertaSistema.TIPOS_ALERTA,
        'niveles': AlertaSistema.NIVELES,
        'lotes': lotes,
        'stats': stats,
        'filtros': {
            'tipo': tipo_alerta,
            'nivel': nivel,
            'prioridad': prioridad,
            'estado': estado,
            'lote': lote_id,
            'leida': leida,
        },
        'is_paginated': alertas_paginadas.has_other_pages(),
        'page_obj': alertas_paginadas,
    }
    
    return render(request, 'aves/alertas_list.html', context)


@login_required
@require_http_methods(["POST"])
def marcar_alerta_leida(request, pk):
    """Marcar alerta como leída."""
    alerta = get_object_or_404(AlertaSistema, pk=pk)
    alerta.leida = True
    alerta.save()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def marcar_alerta_resuelta(request, pk):
    """Marcar alerta como resuelta (desactivar)."""
    alerta = get_object_or_404(AlertaSistema, pk=pk)
    alerta.is_active = False
    alerta.save()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def marcar_alertas_masivo(request):
    """Marcar múltiples alertas como leídas o resueltas."""
    import json
    data = json.loads(request.body)
    
    # Corregir los nombres de parámetros
    alertas_ids = data.get('alertas_ids', []) or data.get('alertas', [])
    accion = data.get('accion')
    
    # Si es "todas", obtener todas las alertas activas
    if alertas_ids == 'todas':
        alertas = AlertaSistema.objects.filter(is_active=True)
        if accion == 'leida':
            alertas.update(leida=True)
        elif accion == 'resuelta':
            alertas.update(is_active=False)
        return JsonResponse({'success': True, 'count': alertas.count()})
    
    # Si son IDs específicos
    if not alertas_ids or not accion:
        return JsonResponse({'success': False, 'error': 'Datos incompletos'})
    
    alertas = AlertaSistema.objects.filter(id__in=alertas_ids)
    
    if accion == 'leida':
        alertas.update(leida=True)
    elif accion == 'resuelta':
        alertas.update(is_active=False)
    else:
        return JsonResponse({'success': False, 'error': 'Acción no válida'})
    
    return JsonResponse({'success': True, 'count': len(alertas_ids)})


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def reportes(request):
    """Vista de reportes."""
    return render(request, 'aves/reportes.html')


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def reporte_produccion(request):
    """Reporte de producción."""
    # Lógica para generar reporte de producción
    lotes = LoteAves.objects.filter(is_active=True)
    
    # Filtros
    lote_id = request.GET.get('lote')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    formato = request.GET.get('formato', 'html')
    
    bitacoras = BitacoraDiaria.objects.select_related('lote')
    
    if lote_id:
        bitacoras = bitacoras.filter(lote_id=lote_id)
    if fecha_desde:
        bitacoras = bitacoras.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        bitacoras = bitacoras.filter(fecha__lte=fecha_hasta)
    
    # Estadísticas
    stats = bitacoras.aggregate(
        total_produccion=Sum('produccion_aaa') + Sum('produccion_aa') + Sum('produccion_a') + 
                        Sum('produccion_b') + Sum('produccion_c'),
        total_mortalidad=Sum('mortalidad'),
        consumo_promedio=Avg('consumo_concentrado'),
    )
    
    if formato == 'pdf':
        return exportar_reporte_pdf('produccion', bitacoras, stats)
    
    context = {
        'bitacoras': bitacoras,
        'lotes': lotes,
        'stats': stats,
        'filtros': {
            'lote': lote_id,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    
    return render(request, 'aves/reporte_produccion.html', context)


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def bitacora_detail(request, pk):
    """Ver detalle de una bitácora diaria."""
    bitacora = get_object_or_404(BitacoraDiaria, pk=pk)
    
    context = {
        'bitacora': bitacora,
    }
    return render(request, 'aves/bitacora_detail.html', context)


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def bitacora_edit(request, pk):
    """Editar bitácora diaria."""
    bitacora = get_object_or_404(BitacoraDiaria, pk=pk)
    
    if request.method == 'POST':
        form = BitacoraDiariaEditForm(request.POST, instance=bitacora)
        
        if form.is_valid():
            # Verificar si realmente hay cambios
            changed_data = [field for field in form.changed_data if field != 'justificacion']
            
            if not changed_data:
                messages.info(request, 'No se detectaron cambios en la bitácora.')
                return redirect('aves:bitacora_detail', pk=bitacora.id)
            
            # Registrar modificación antes de guardar
            valores_anteriores = {}
            valores_nuevos = {}
            
            for field in changed_data:
                valores_anteriores[field] = getattr(bitacora, field)
                valores_nuevos[field] = form.cleaned_data[field]
            
            bitacora_actualizada = form.save()
            
            # Crear registro de modificación
            RegistroModificacion.objects.create(
                usuario=request.user,
                modelo='BitacoraDiaria',
                objeto_id=bitacora.id,
                accion='UPDATE',
                campos_modificados=changed_data,
                valores_anteriores=valores_anteriores,
                valores_nuevos=valores_nuevos,
                justificacion=form.cleaned_data['justificacion']
            )
            
            messages.success(request, 'Bitácora actualizada exitosamente.')
            return redirect('aves:bitacora_detail', pk=bitacora.id)
        else:
            messages.error(request, 'Error al actualizar la bitácora. Verifique los datos.')
    else:
        form = BitacoraDiariaEditForm(instance=bitacora)
    
    context = {
        'form': form,
        'bitacora': bitacora,
        'is_edit': True,
    }
    return render(request, 'aves/bitacora_form.html', context)


@login_required
@role_required(['superusuario', 'punto_blanco'])
def actualizar_stock_automatico(request):
    """Vista AJAX para actualizar stocks mínimos automáticamente."""
    if request.method == 'POST':
        try:
            inventarios_actualizados = 0
            
            for inventario in InventarioHuevos.objects.filter(stock_automatico=True):
                if inventario.actualizar_stock_minimo():
                    inventarios_actualizados += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Se actualizaron {inventarios_actualizados} inventarios automáticamente.',
                'inventarios_actualizados': inventarios_actualizados
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar stocks: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
@role_required(['superusuario', 'punto_blanco'])
def configurar_stock_automatico(request, inventario_id):
    """Vista para configurar el stock automático de un inventario específico."""
    inventario = get_object_or_404(InventarioHuevos, id=inventario_id)
    
    if request.method == 'POST':
        try:
            stock_automatico = request.POST.get('stock_automatico') == 'true'
            factor_calculo = float(request.POST.get('factor_calculo', 0.75))
            dias_stock = int(request.POST.get('dias_stock', 3))
            
            inventario.stock_automatico = stock_automatico
            inventario.factor_calculo = factor_calculo
            inventario.dias_stock = dias_stock
            
            if stock_automatico:
                inventario.cantidad_minima = inventario.calcular_stock_minimo_automatico()
            
            inventario.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Configuración actualizada correctamente.',
                'nuevo_stock_minimo': inventario.cantidad_minima_calculada
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar configuración: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def movimiento_huevos_list(request):
    """Lista de movimientos de huevos."""
    movimientos = MovimientoHuevos.objects.select_related('usuario_registro').prefetch_related('detalles').order_by('-fecha')
    
    # Filtros
    tipo_movimiento = request.GET.get('tipo_movimiento')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if tipo_movimiento:
        movimientos = movimientos.filter(tipo_movimiento=tipo_movimiento)
    if fecha_desde:
        movimientos = movimientos.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        movimientos = movimientos.filter(fecha__lte=fecha_hasta)
    
    paginator = Paginator(movimientos, 20)
    page = request.GET.get('page')
    movimientos = paginator.get_page(page)
    
    context = {
        'movimientos': movimientos,
        'tipos_movimiento': MovimientoHuevos.TIPOS_MOVIMIENTO,
    }
    
    return render(request, 'aves/movimiento_huevos_list.html', context)


@login_required
@role_required(['superusuario', 'veterinario', 'solo_vista'])
def plan_vacunacion_detail(request, pk):
    """Detalle del plan de vacunación."""
    plan = get_object_or_404(PlanVacunacion.objects.select_related('lote', 'tipo_vacuna', 'veterinario'), pk=pk)
    
    context = {
        'plan': plan,
    }
    
    return render(request, 'aves/plan_vacunacion_detail.html', context)


@login_required
@role_required(['superusuario', 'veterinario'])
@require_http_methods(["POST"])
def plan_vacunacion_aplicar(request, pk):
    """Marcar plan de vacunación como aplicado."""
    plan = get_object_or_404(PlanVacunacion, pk=pk)
    
    try:
        fecha_aplicada = request.POST.get('fecha_aplicada')
        numero_aves_vacunadas = request.POST.get('numero_aves_vacunadas')
        lote_vacuna = request.POST.get('lote_vacuna', '')
        observaciones = request.POST.get('observaciones', '')
        
        if not fecha_aplicada or not numero_aves_vacunadas:
            return JsonResponse({'success': False, 'error': 'Fecha y número de aves son requeridos'})
        
        # Convertir fecha
        from datetime import datetime
        fecha_aplicada = datetime.strptime(fecha_aplicada, '%Y-%m-%d').date()
        
        # Actualizar el plan
        plan.fecha_aplicada = fecha_aplicada
        plan.numero_aves_vacunadas = int(numero_aves_vacunadas)
        plan.lote_vacuna = lote_vacuna
        plan.observaciones = observaciones
        plan.aplicada = True
        plan.save()
        
        messages.success(request, f'Vacuna {plan.tipo_vacuna.nombre} marcada como aplicada exitosamente.')
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
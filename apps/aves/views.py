"""
Vistas para el módulo avícola.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json

from apps.usuarios.decorators import role_required
from .models import *
from .forms import *
from .utils import generar_alertas, actualizar_inventario_huevos, exportar_reporte_pdf


@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario', 'solo_vista'])
def dashboard_aves(request):
    """Dashboard principal del módulo avícola."""
    # Estadísticas generales
    total_lotes = LoteAves.objects.filter(is_active=True).count()
    total_aves = LoteAves.objects.filter(is_active=True).aggregate(
        total=Sum('numero_aves_actual'))['total'] or 0
    
    # Producción del día
    hoy = timezone.now().date()
    produccion_hoy = BitacoraDiaria.objects.filter(fecha=hoy).aggregate(
        total=Sum('produccion_aaa') + Sum('produccion_aa') + Sum('produccion_a') + 
              Sum('produccion_b') + Sum('produccion_c'))['total'] or 0
    
    # Alertas pendientes
    alertas_pendientes = AlertaSistema.objects.filter(leida=False).count()
    
    # Vacunas pendientes
    vacunas_pendientes = PlanVacunacion.objects.filter(
        aplicada=False, 
        fecha_programada__lte=hoy + timedelta(days=7)
    ).count()
    
    # Inventario de huevos
    inventario_huevos = InventarioHuevos.objects.all()
    
    context = {
        'total_lotes': total_lotes,
        'total_aves': total_aves,
        'produccion_hoy': produccion_hoy,
        'alertas_pendientes': alertas_pendientes,
        'vacunas_pendientes': vacunas_pendientes,
        'inventario_huevos': inventario_huevos,
    }
    
    return render(request, 'aves/dashboard.html', context)


@login_required
@role_required(['superusuario', 'admin_aves'])
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
@role_required(['superusuario', 'admin_aves'])
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
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
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
@role_required(['superusuario', 'punto_blanco', 'solo_vista'])
def inventario_huevos(request):
    """Vista de inventario de huevos."""
    inventarios = InventarioHuevos.objects.all()
    
    # Movimientos recientes
    movimientos_recientes = MovimientoHuevos.objects.select_related('usuario_registro').order_by('-fecha')[:20]
    
    context = {
        'inventarios': inventarios,
        'movimientos_recientes': movimientos_recientes,
    }
    
    return render(request, 'aves/inventario_huevos.html', context)


@login_required
@role_required(['superusuario', 'admin_aves'])
def movimiento_huevos_create(request):
    """Crear movimiento de huevos."""
    if request.method == 'POST':
        form = MovimientoHuevosForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario_registro = request.user
            movimiento.save()
            
            # Actualizar inventario
            inventario = InventarioHuevos.objects.get(categoria=movimiento.categoria_huevo)
            if movimiento.tipo_movimiento in ['venta', 'autoconsumo', 'baja']:
                inventario.cantidad_actual -= movimiento.cantidad
            else:  # devolución
                inventario.cantidad_actual += movimiento.cantidad
            inventario.save()
            
            messages.success(request, 'Movimiento de huevos registrado exitosamente.')
            return redirect('aves:inventario_huevos')
        else:
            messages.error(request, 'Error al registrar el movimiento. Verifique los datos.')
    else:
        form = MovimientoHuevosForm()
    
    return render(request, 'aves/movimiento_huevos_form.html', {'form': form})


@login_required
@role_required(['superusuario', 'veterinario'])
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
@role_required(['superusuario', 'veterinario'])
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
    
    return render(request, 'aves/plan_vacunacion_form.html', {'form': form})


@login_required
@role_required(['superusuario', 'admin_aves', 'solo_vista'])
def alertas_list(request):
    """Lista de alertas del sistema."""
    alertas = AlertaSistema.objects.select_related('lote', 'galpon', 'usuario_destinatario').order_by('-fecha_generacion')
    
    # Filtros
    tipo_alerta = request.GET.get('tipo')
    nivel = request.GET.get('nivel')
    leida = request.GET.get('leida')
    
    if tipo_alerta:
        alertas = alertas.filter(tipo_alerta=tipo_alerta)
    if nivel:
        alertas = alertas.filter(nivel=nivel)
    if leida == 'true':
        alertas = alertas.filter(leida=True)
    elif leida == 'false':
        alertas = alertas.filter(leida=False)
    
    paginator = Paginator(alertas, 20)
    page = request.GET.get('page')
    alertas = paginator.get_page(page)
    
    context = {
        'alertas': alertas,
        'tipos_alerta': AlertaSistema.TIPOS_ALERTA,
        'niveles': AlertaSistema.NIVELES,
        'filtros': {
            'tipo': tipo_alerta,
            'nivel': nivel,
            'leida': leida,
        }
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
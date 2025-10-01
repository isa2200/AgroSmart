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
from django.core.exceptions import ValidationError
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
    
    # Producción total (inventario de huevos)
    produccion_total = InventarioHuevos.objects.aggregate(
        total=Sum('cantidad_actual'))['total'] or 0
    
    # Alertas pendientes
    alertas_pendientes = AlertaSistema.objects.filter(leida=False).count()
    
    # Vacunas pendientes
    hoy = timezone.now().date()
    vacunas_pendientes = PlanVacunacion.objects.filter(
        aplicada=False, 
        fecha_programada__lte=hoy + timedelta(days=7)
    ).count()
    
    # Inventario de huevos
    inventario_huevos = InventarioHuevos.objects.all()
    
    context = {
        'total_lotes': total_lotes,
        'total_aves': total_aves,
        'produccion_total': produccion_total,
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
    
    # Movimientos recientes - obtener detalles en lugar de movimientos principales
    movimientos_recientes = DetalleMovimientoHuevos.objects.select_related(
        'movimiento__usuario_registro', 'movimiento'
    ).order_by('-movimiento__fecha')[:20]
    
    context = {
        'inventarios': inventarios,
        'movimientos_recientes': movimientos_recientes,
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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, F, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
import json
import base64
from apps.usuarios.decorators import role_required
from .models import LotePorcino, BitacoraDiariaPorcinos, AlertaPorcinos, TareaPorcinos, AnimalPorcino, InventarioPorcino, PlanVacunacion
from .forms import LotePorcinoForm, BitacoraDiariaPorcinosForm, TareaPorcinosForm, AnimalPorcinoForm, PlanVacunacionForm

@login_required
@role_required(['superusuario', 'admin_porcinos', 'practicante_porcinos', 'veterinario', 'solo_vista'])
def dashboard(request):
    # Si es veterinario, redirigir directamente al plan de vacunación
    if request.user.perfilusuario.rol == 'veterinario':
        return redirect('porcinos:plan_vacunacion_list')
        
    total_lotes = LotePorcino.objects.filter(is_active=True).count()
    total_cerdos = LotePorcino.objects.filter(is_active=True).aggregate(total=Sum('numero_cerdos_actual'))['total'] or 0
    
    # Tareas
    tareas_pendientes = TareaPorcinos.objects.filter(estado='pendiente').order_by('fecha_limite')
    
    # Alertas
    alertas_criticas = AlertaPorcinos.objects.filter(is_active=True, nivel='critica').count()
    alertas_normales = AlertaPorcinos.objects.filter(is_active=True, nivel='normal').count()
    
    context = {
        'total_lotes': total_lotes,
        'total_cerdos': total_cerdos,
        'tareas_pendientes': tareas_pendientes,
        'alertas_criticas': alertas_criticas,
        'alertas_normales': alertas_normales,
        'tarea_form': TareaPorcinosForm(),
    }
    return render(request, 'porcinos/dashboard.html', context)

@login_required
@role_required(['superusuario', 'admin_porcinos', 'practicante_porcinos', 'veterinario', 'solo_vista'])
def lote_list(request):
    lotes = LotePorcino.objects.filter(is_active=True).order_by('-fecha_llegada')
    estado = request.GET.get('estado')
    corral = request.GET.get('corral')
    if estado:
        lotes = lotes.filter(estado=estado)
    if corral:
        lotes = lotes.filter(corral__icontains=corral)
    paginator = Paginator(lotes, 20)
    page = request.GET.get('page')
    lotes = paginator.get_page(page)
    context = {
        'lotes': lotes,
        'filtros': {
            'estado': estado,
            'corral': corral,
        }
    }
    return render(request, 'porcinos/lote_list.html', context)

@login_required
@role_required(['superusuario', 'admin_porcinos'])
def lote_create(request):
    if request.method == 'POST':
        form = LotePorcinoForm(request.POST)
        if form.is_valid():
            lote = form.save()
            messages.success(request, 'Lote creado correctamente')
            return redirect('porcinos:lote_list')
        else:
            messages.error(request, 'Revise los campos del formulario')
    else:
        form = LotePorcinoForm()
    return render(request, 'porcinos/lote_form.html', {'form': form, 'title': 'Crear Lote'})

@login_required
@role_required(['superusuario', 'admin_porcinos', 'practicante_porcinos', 'veterinario', 'solo_vista', 'punto_blanco'])
def lote_detail(request, pk):
    lote = get_object_or_404(LotePorcino, pk=pk)
    animales = AnimalPorcino.objects.filter(lote=lote, is_active=True)
    bitacoras = BitacoraDiariaPorcinos.objects.filter(lote=lote, is_active=True).order_by('-fecha')[:10]
    
    # Estadísticas básicas del lote
    total_animales = animales.count()
    
    context = {
        'lote': lote,
        'animales': animales,
        'bitacoras': bitacoras,
        'total_animales': total_animales
    }
    return render(request, 'porcinos/lote_detail.html', context)

@login_required
@role_required(['superusuario', 'admin_porcinos'])
def lote_edit(request, pk):
    lote = get_object_or_404(LotePorcino, pk=pk)
    if request.method == 'POST':
        form = LotePorcinoForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()

from .models import PlanVacunacion
from .forms import PlanVacunacionForm

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario', 'solo_vista', 'punto_blanco'])
def plan_vacunacion_list(request):
    planes = PlanVacunacion.objects.filter(is_active=True).order_by('fecha_programada')
    return render(request, 'porcinos/plan_vacunacion_list.html', {'planes': planes})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario'])
def plan_vacunacion_create(request):
    if request.method == 'POST':
        form = PlanVacunacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan de vacunación creado correctamente')
            return redirect('porcinos:plan_vacunacion_list')
        else:
            messages.error(request, 'Revise los campos del formulario')
    else:
        form = PlanVacunacionForm()
    return render(request, 'porcinos/plan_vacunacion_form.html', {'form': form, 'title': 'Crear Plan de Vacunación'})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario'])
def plan_vacunacion_update(request, pk):
    plan = get_object_or_404(PlanVacunacion, pk=pk)
    if request.method == 'POST':
        form = PlanVacunacionForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan de vacunación actualizado correctamente')
            return redirect('porcinos:plan_vacunacion_list')
        else:
            messages.error(request, 'Revise los campos del formulario')
    else:
        form = PlanVacunacionForm(instance=plan)
    return render(request, 'porcinos/plan_vacunacion_form.html', {'form': form, 'title': 'Editar Plan de Vacunación'})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario'])
def plan_vacunacion_delete(request, pk):
    plan = get_object_or_404(PlanVacunacion, pk=pk)
    plan.is_active = False
    plan.save()
    messages.success(request, 'Plan de vacunación eliminado correctamente')
    return redirect('porcinos:plan_vacunacion_list')

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario'])
def lote_update(request, pk):
    lote = get_object_or_404(LotePorcino, pk=pk)
    if request.method == 'POST':
        form = LotePorcinoForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lote actualizado')
            return redirect('porcinos:lote_list')
    else:
        form = LotePorcinoForm(instance=lote)
    return render(request, 'porcinos/lote_edit.html', {'form': form, 'lote': lote, 'title': 'Editar Lote'})

@login_required
@role_required(['superusuario'])
def lote_delete(request, pk):
    lote = get_object_or_404(LotePorcino, pk=pk)
    if request.method == 'POST':
        lote.is_active = False # Soft delete
        lote.save()
        messages.success(request, 'Lote eliminado')
        return redirect('porcinos:lote_list')
    return render(request, 'porcinos/lote_delete_confirm.html', {'lote': lote})

@login_required
@role_required(['superusuario', 'solo_vista'])
def bitacora_list(request):
    registros = BitacoraDiariaPorcinos.objects.select_related('lote').order_by('-fecha')
    lote_id = request.GET.get('lote')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    if lote_id:
        registros = registros.filter(lote_id=lote_id)
    if fecha_desde:
        registros = registros.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        registros = registros.filter(fecha__lte=fecha_hasta)
    paginator = Paginator(registros, 20)
    page = request.GET.get('page')
    registros = paginator.get_page(page)
    context = {
        'bitacoras': registros,
        'lotes': LotePorcino.objects.filter(is_active=True),
        'filtros': {
            'lote': lote_id,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    return render(request, 'porcinos/bitacora_list.html', context)

@login_required
@role_required(['superusuario'])
def bitacora_create(request):
    if request.method == 'POST':
        form = BitacoraDiariaPorcinosForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario_registro = request.user
            obj.save()
            messages.success(request, 'Bitácora registrada')
            return redirect('porcinos:bitacora_list')
        else:
            messages.error(request, 'Revise los campos del formulario')
    else:
        form = BitacoraDiariaPorcinosForm()
    return render(request, 'porcinos/bitacora_form.html', {'form': form})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario', 'solo_vista', 'punto_blanco'])
def bitacora_detail(request, pk):
    bitacora = get_object_or_404(BitacoraDiariaPorcinos, pk=pk)
    return render(request, 'porcinos/bitacora_detail.html', {'bitacora': bitacora})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario'])
def bitacora_update(request, pk):
    bitacora = get_object_or_404(BitacoraDiariaPorcinos, pk=pk)
    if request.method == 'POST':
        form = BitacoraDiariaPorcinosForm(request.POST, request.FILES, instance=bitacora)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bitácora actualizada correctamente')
            return redirect('porcinos:bitacora_detail', pk=pk)
    else:
        form = BitacoraDiariaPorcinosForm(instance=bitacora)
    return render(request, 'porcinos/bitacora_form.html', {'form': form})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario', 'solo_vista', 'punto_blanco'])
def inventario_permanente(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle file upload (Signature)
        if request.FILES.get('firma_realizado'):
            try:
                registro_id = request.POST.get('id')
                firma = request.FILES.get('firma_realizado')
                
                if registro_id:
                    registro = get_object_or_404(InventarioPorcino, id=registro_id)
                    registro.firma_realizado = firma
                    registro.save()
                    return JsonResponse({'status': 'success', 'url': registro.firma_realizado.url})
                return JsonResponse({'status': 'error', 'message': 'ID no proporcionado'}, status=400)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        # Handle JSON data (Inline text edit)
        try:
            data = json.loads(request.body)
            registro_id = data.get('id')
            campo = data.get('field')
            valor = data.get('value')

            if registro_id:
                registro = get_object_or_404(InventarioPorcino, id=registro_id)

                campos_numericos = [
                    'madre', 'reproductores', 'hembras_reemplazo', 'hembras_gestacion',
                    'hembras_lactando', 'lechones_lactando', 'preiniciador', 'levante_ceba',
                    'descartes', 'lechones_vivos', 'lechones_muertos', 'destetes',
                    'compras', 'ventas', 'salidas', 'muertes'
                ]

                if campo in campos_numericos:
                    setattr(registro, campo, int(valor) if valor else 0)
                elif campo == 'detalle':
                    registro.detalle = valor

                # Recalculate total if needed (though model might not have auto-calc property, let's do it here or assume logic exists)
                # Porcinos model has a 'total' field, not property. We should update it.
                # Total logic from previous code or assumption? 
                # Aves model has a property. Porcinos model has a field 'total'.
                # Let's update the total.
                # Total = Sum of population categories?
                # Based on Porcinos model fields:
                registro.total = (
                    registro.madre + registro.reproductores + registro.hembras_reemplazo +
                    registro.hembras_gestacion + registro.hembras_lactando + 
                    registro.lechones_lactando + registro.preiniciador + 
                    registro.levante_ceba + registro.descartes
                )
                
                registro.save()

                return JsonResponse({'status': 'success', 'new_total': registro.total})

            return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    if request.method == 'POST':
        data_str = request.POST.get('inventario_json')
        if data_str:
            try:
                data = json.loads(data_str)
                # Create object
                inv = InventarioPorcino(
                    fecha=f"{data.get('ano')}-{data.get('mes')}-{data.get('dia')}",
                    detalle=data.get('detalle', ''),
                    madre=int(data.get('madre') or 0),
                    reproductores=int(data.get('reproductores') or 0),
                    hembras_reemplazo=int(data.get('hembras_reemplazo') or 0),
                    hembras_gestacion=int(data.get('hembras_gestacion') or 0),
                    hembras_lactando=int(data.get('hembras_lactando') or 0),
                    lechones_lactando=int(data.get('lechones_lactando') or 0),
                    preiniciador=int(data.get('preiniciador') or 0),
                    levante_ceba=int(data.get('levante_ceba') or 0),
                    descartes=int(data.get('descartes') or 0),
                    lechones_vivos=int(data.get('lechones_vivos') or 0),
                    lechones_muertos=int(data.get('lechones_muertos') or 0),
                    destetes=int(data.get('destetes') or 0),
                    compras=int(data.get('compras') or 0),
                    ventas=int(data.get('ventas') or 0),
                    salidas=int(data.get('salidas') or 0),
                    muertes=int(data.get('muertes') or 0),
                    total=int(data.get('total') or 0),
                    realizado_por=data.get('sig_realizado_nombre', ''),
                    revisado_por=data.get('sig_revisado_nombre', ''),
                    aprobado_por=data.get('sig_aprobado_nombre', ''),
                    usuario_registro=request.user
                )
                
                # Handle signatures
                def save_sig(b64_str, field):
                    if b64_str and 'base64,' in b64_str:
                        format, imgstr = b64_str.split(';base64,') 
                        ext = format.split('/')[-1] 
                        data = ContentFile(base64.b64decode(imgstr), name=f'sig_{field}_{timezone.now().timestamp()}.{ext}')
                        setattr(inv, field, data)

                save_sig(data.get('sig_realizado_b64'), 'firma_realizado')
                save_sig(data.get('sig_revisado_b64'), 'firma_revisado')
                save_sig(data.get('sig_aprobado_b64'), 'firma_aprobado')

                inv.save()
                messages.success(request, 'Inventario registrado correctamente')
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
        
        return redirect('porcinos:inventario_permanente')

    # GET request
    registros = InventarioPorcino.objects.filter(is_active=True).order_by('-fecha')

    # Filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio:
        registros = registros.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        registros = registros.filter(fecha__lte=fecha_fin)
    
    # Prepare JSON for table
    registros_data = []
    for r in registros:
        registros_data.append({
            'ano': r.fecha.year,
            'mes': r.fecha.month,
            'dia': r.fecha.day,
            'detalle': r.detalle,
            'madre': r.madre,
            'lechones_vivos': r.lechones_vivos,
            'lechones_muertos': r.lechones_muertos,
            'compras': r.compras,
            'ventas': r.ventas,
            'salidas': r.salidas,
            'muertes': r.muertes,
            'preiniciador': r.preiniciador,
            'levante_ceba': r.levante_ceba,
            'reproductores': r.reproductores,
            'hembras_reemplazo': r.hembras_reemplazo,
            'hembras_gestacion': r.hembras_gestacion,
            'destetes': r.destetes,
            'hembras_lactando': r.hembras_lactando,
            'lechones_lactando': r.lechones_lactando,
            'descartes': r.descartes,
            'total': r.total,
            'sig_realizado_nombre': r.realizado_por,
            'sig_revisado_nombre': r.revisado_por,
            'sig_aprobado_nombre': r.aprobado_por,
            'sig_realizado_b64': r.firma_realizado.url if r.firma_realizado else '',
            'sig_revisado_b64': r.firma_revisado.url if r.firma_revisado else '',
            'sig_aprobado_b64': r.firma_aprobado.url if r.firma_aprobado else '',
        })
    
    borrador_json = "{}"
    load_index = request.GET.get('load_index')
    if load_index is not None:
        try:
            idx = int(load_index)
            if 0 <= idx < len(registros_data):
                borrador_json = json.dumps(registros_data[idx])
        except:
            pass

    context = {
        'registros': registros,
        'inventarios_json': json.dumps(registros_data),
        'borrador_json': borrador_json,
        'rango_print': range(15),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'porcinos/inventario_permanente.html', context)

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario', 'punto_blanco'])
def registro_alimento(request):
    return render(request, 'porcinos/registro_alimento.html')

@login_required
def plan_sanitario_gestante(request):
    return render(request, 'porcinos/plan_sanitario_gestante.html')

@login_required
def alertas_list(request):
    alertas = AlertaPorcinos.objects.filter(is_active=True).order_by('-created_at')
    
    # Contadores
    criticas = alertas.filter(nivel='critica').count()
    normales = alertas.filter(nivel='normal').count()
    
    context = {
        'alertas': alertas,
        'criticas': criticas,
        'normales': normales,
    }
    return render(request, 'porcinos/alertas_list.html', context)

@login_required
def marcar_alerta_leida(request, alerta_id):
    alerta = get_object_or_404(AlertaPorcinos, pk=alerta_id)
    alerta.leida = True # Asumiendo que existe campo leida, o se borra/archiva
    # Si no hay campo leida, tal vez se usa is_active=False
    alerta.is_active = False
    alerta.save()
    messages.success(request, 'Alerta marcada como leída')
    return redirect('porcinos:alertas_list')

@login_required
def marcar_alertas_masivo(request):
    if request.method == 'POST':
        ids = request.POST.getlist('alerta_ids')
        AlertaPorcinos.objects.filter(id__in=ids).update(is_active=False)
        messages.success(request, 'Alertas actualizadas')
    return redirect('porcinos:alertas_list')

@login_required
def reportes(request):
    return render(request, 'porcinos/reportes.html')

@login_required
def reporte_produccion(request):
    return render(request, 'porcinos/reporte_produccion.html')

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario', 'solo_vista', 'punto_blanco'])
def animal_list(request):
    queryset = AnimalPorcino.objects.filter(is_active=True).order_by('-created_at')
    
    # Filtros
    q = request.GET.get('q')
    etapa = request.GET.get('etapa')
    sexo = request.GET.get('sexo')
    
    if q:
        queryset = queryset.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q))
    if etapa:
        queryset = queryset.filter(etapa=etapa)
    if sexo:
        queryset = queryset.filter(sexo=sexo)
    
    paginator = Paginator(queryset, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'etapa_choices': AnimalPorcino.ETAPA_CHOICES,
        'sexo_choices': AnimalPorcino.SEXO_CHOICES,
    }
    return render(request, 'porcinos/animal_list.html', context)

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario'])
def animal_create(request):
    if request.method == 'POST':
        form = AnimalPorcinoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Animal registrado correctamente')
            return redirect('porcinos:animal_list')
    else:
        form = AnimalPorcinoForm()
    return render(request, 'porcinos/animal_form.html', {'form': form, 'title': 'Registrar Animal'})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario', 'solo_vista', 'punto_blanco'])
def animal_detail(request, pk):
    animal = get_object_or_404(AnimalPorcino, pk=pk)
    return render(request, 'porcinos/animal_detail.html', {'animal': animal})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario'])
def animal_update(request, pk):
    animal = get_object_or_404(AnimalPorcino, pk=pk)
    if request.method == 'POST':
        form = AnimalPorcinoForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Animal actualizado')
            return redirect('porcinos:animal_list')
    else:
        form = AnimalPorcinoForm(instance=animal)
    return render(request, 'porcinos/animal_form.html', {'form': form, 'title': 'Editar Animal', 'animal': animal})

@login_required
@role_required(['superusuario', 'admin_aves'])
def animal_delete(request, pk):
    animal = get_object_or_404(AnimalPorcino, pk=pk)
    if request.method == 'POST':
        animal.is_active = False
        animal.save()
        messages.success(request, 'Animal eliminado')
        return redirect('porcinos:animal_list')
    return render(request, 'porcinos/animal_confirm_delete.html', {'animal': animal})

@login_required
def crear_tarea(request):
    if request.method == 'POST':
        form = TareaPorcinosForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            if not tarea.responsable:
                tarea.responsable = request.user
            tarea.creado_por = request.user
            tarea.save()
            messages.success(request, 'Tarea creada exitosamente.')
        else:
            messages.error(request, 'Error al crear la tarea.')
    return redirect('porcinos:dashboard')

@login_required
def completar_tarea(request, tarea_id):
    tarea = get_object_or_404(TareaPorcinos, id=tarea_id)
    tarea.estado = 'completada'
    tarea.save()
    messages.success(request, 'Tarea completada.')
    return redirect('porcinos:dashboard')

@login_required
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(TareaPorcinos, id=tarea_id)
    tarea.delete()
    messages.success(request, 'Tarea eliminada.')
    return redirect('porcinos:dashboard')

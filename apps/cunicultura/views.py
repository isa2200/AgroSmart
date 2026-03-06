from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.utils import timezone
from datetime import timedelta
import json
from apps.usuarios.decorators import role_required
from .models import InventarioConejos, LibroDiarioConejos, ControlDestetes, RegistroAlimentoConejos, BitacoraActividadesConejos, PrecioConejo, HistorialInventarioConejos, TareaCunicultura, PlanVacunacion
from .forms import InventarioConejosForm, LibroDiarioConejosForm, ControlDestetesForm, RegistroAlimentoConejosForm, BitacoraActividadesConejosForm, TareaCuniculturaForm, PlanVacunacionForm

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario', 'solo_vista'])
def dashboard_cunicultura(request):
    """
    Dashboard principal del módulo de cunicultura.
    Muestra métricas generales y acceso a los diferentes submódulos.
    """
    # Si es veterinario, redirigir directamente al plan de vacunación
    if request.user.perfilusuario.rol == 'veterinario':
        return redirect('cunicultura:plan_vacunacion_list')

    # Manejo de actualizaciones de precios via AJAX
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            precio_id = data.get('id')
            field = data.get('field')
            value = data.get('value')
            
            precio = PrecioConejo.objects.get(id=precio_id)
            
            if field == 'descripcion':
                precio.descripcion = value
            elif field == 'edad_dias':
                precio.edad_dias = value
            elif field == 'valor':
                precio.valor = value
                
            precio.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # Obtener el último registro de inventario para las métricas actuales
    ultimo_inventario = InventarioConejos.objects.order_by('-fecha', '-id').first()
    
    total_conejos = 0
    reproductores = 0
    gazapos = 0
    levante_ceba = 0
    
    if ultimo_inventario:
        reproductores = (ultimo_inventario.reproductores + 
                        ultimo_inventario.hembra_reemplazo + 
                        ultimo_inventario.hembra_no_lactando + 
                        ultimo_inventario.hembra_lactando)
        gazapos = ultimo_inventario.gazapos
        levante_ceba = (ultimo_inventario.macho_levante_ceba + 
                       ultimo_inventario.hembra_levante_ceba)
        total_conejos = ultimo_inventario.total
    
    # Precios para la tabla de precios (si existe en el dashboard)
    precios = PrecioConejo.objects.all().order_by('orden')

    # Últimas actividades/novedades
    ultimas_actividades = BitacoraActividadesConejos.objects.all().order_by('-fecha', '-id')[:5]

    # Tareas Pendientes
    tareas = TareaCunicultura.objects.exclude(estado='completada').order_by('-prioridad', 'fecha_limite')
    tarea_form = TareaCuniculturaForm()
    
    context = {
        'total_conejos': total_conejos,
        'reproductores': reproductores,
        'gazapos': gazapos,
        'levante_ceba': levante_ceba,
        'ultimo_inventario': ultimo_inventario,
        'precios': precios,
        'ultimas_actividades': ultimas_actividades,
        'tareas': tareas,
        'tarea_form': tarea_form,
    }
    return render(request, 'cunicultura/dashboard.html', context)

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario', 'solo_vista', 'punto_blanco'])
def inventario_permanente(request):
    """
    Vista para el Inventario Permanente de Conejos
    """
    registros = InventarioConejos.objects.all().order_by('-fecha', '-id')
    
    # Filtros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        registros = registros.filter(fecha__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        registros = registros.filter(fecha__gte=fecha_inicio)

    if request.method == 'POST':
        if 'eliminar' in request.POST:
            registro_id = request.POST.get('id') or request.POST.get('eliminar')
            justificacion = request.POST.get('justificacion')
            
            registro = get_object_or_404(InventarioConejos, id=registro_id)
            
            # Guardar estado anterior
            datos_anteriores = model_to_dict(registro)
            datos_anteriores['fecha'] = str(datos_anteriores['fecha'])
            
            # Registrar historial ANTES de eliminar
            HistorialInventarioConejos.objects.create(
                usuario=request.user,
                accion='ELIMINAR',
                justificacion=justificacion,
                registro_id=registro.id,
                fecha_registro=registro.fecha,
                detalle_registro=registro.detalle,
                datos_anteriores=json.dumps(datos_anteriores, default=str)
            )
            
            registro.delete()
            messages.success(request, 'Registro eliminado correctamente')
            return redirect('cunicultura:inventario_permanente')
            
        else: # Crear nuevo
            form = InventarioConejosForm(request.POST, request.FILES)
            if form.is_valid():
                registro = form.save()
                # Opcional: Registrar creación
                HistorialInventarioConejos.objects.create(
                    usuario=request.user,
                    accion='CREAR',
                    registro_id=registro.id,
                    fecha_registro=registro.fecha,
                    detalle_registro=registro.detalle
                )
                messages.success(request, 'Registro creado correctamente')
                return redirect('cunicultura:inventario_permanente')
    else:
        form = InventarioConejosForm()
        
    context = {
        'registros': registros,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'cunicultura/inventario_permanente.html', context)

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario', 'solo_vista', 'punto_blanco'])
def historial_inventario(request):
    historial = HistorialInventarioConejos.objects.all().order_by('-fecha_accion')
    return render(request, 'cunicultura/historial_inventario.html', {'historial': historial})

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario', 'solo_vista', 'punto_blanco'])
def libro_diario(request):
    """
    Vista para el Libro Diario de Conejos
    """
    registros = LibroDiarioConejos.objects.all().order_by('-fecha', '-id')
    
    # Filtros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        registros = registros.filter(fecha__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        registros = registros.filter(fecha__gte=fecha_inicio)
    elif fecha_fin:
        registros = registros.filter(fecha__lte=fecha_fin)
    
    if request.method == 'POST':
        form = LibroDiarioConejosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cunicultura:libro_diario')
    else:
        form = LibroDiarioConejosForm()
        
    context = {
        'registros': registros,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'cunicultura/libro_diario.html', context)

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario', 'solo_vista', 'punto_blanco'])
def control_destetes(request):
    """
    Vista para el Control de Destetes
    """
    registros = ControlDestetes.objects.all().order_by('-fecha_destete', '-id')
    
    # Filtros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        registros = registros.filter(fecha_destete__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        registros = registros.filter(fecha_destete__gte=fecha_inicio)
    elif fecha_fin:
        registros = registros.filter(fecha_destete__lte=fecha_fin)
    
    if request.method == 'POST':
        form = ControlDestetesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cunicultura:control_destetes')
    else:
        form = ControlDestetesForm()
        
    context = {
        'registros': registros,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'cunicultura/control_destetes.html', context)

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario', 'solo_vista', 'punto_blanco'])
def registro_alimento(request):
    """
    Vista para el Registro de Alimento de Conejos
    """
    registros = RegistroAlimentoConejos.objects.all().order_by('-fecha', '-id')
    
    # Filtros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        registros = registros.filter(fecha__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        registros = registros.filter(fecha__gte=fecha_inicio)
    elif fecha_fin:
        registros = registros.filter(fecha__lte=fecha_fin)
    
    if request.method == 'POST':
        form = RegistroAlimentoConejosForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            # Calcular saldo basico
            # Buscamos el último registro anterior a la fecha actual para obtener saldo inicial
            ultimo = RegistroAlimentoConejos.objects.filter(fecha__lte=registro.fecha).exclude(id=registro.id).order_by('-fecha', '-id').first()
            saldo_anterior = ultimo.saldo if ultimo else 0
            registro.saldo = saldo_anterior + registro.entrada - registro.salida
            registro.save()
            return redirect('cunicultura:registro_alimento')
    else:
        form = RegistroAlimentoConejosForm()
    
    context = {
        'registros': registros,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'cunicultura/registro_alimento.html', context)

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario', 'solo_vista', 'punto_blanco'])
def bitacora_actividades(request):
    """
    Vista para la Bitácora de Actividades de Conejos
    """
    registros = BitacoraActividadesConejos.objects.all().order_by('-fecha', '-id')
    
    # Filtros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        registros = registros.filter(fecha__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        registros = registros.filter(fecha__gte=fecha_inicio)
    elif fecha_fin:
        registros = registros.filter(fecha__lte=fecha_fin)
    
    if request.method == 'POST':
        form = BitacoraActividadesConejosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cunicultura:bitacora_actividades')
    else:
        form = BitacoraActividadesConejosForm()
    
    context = {
        'registros': registros,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'cunicultura/bitacora_actividades.html', context)

@login_required
def crear_tarea(request):
    if request.method == 'POST':
        form = TareaCuniculturaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            if not tarea.responsable:
                tarea.responsable = request.user
            tarea.creado_por = request.user
            tarea.save()
            messages.success(request, 'Tarea creada exitosamente.')
        else:
            messages.error(request, 'Error al crear la tarea. Verifique los datos.')
    return redirect('cunicultura:dashboard')

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario'])
def completar_tarea(request, tarea_id):
    tarea = get_object_or_404(TareaCunicultura, id=tarea_id)
    tarea.estado = 'completada'
    tarea.save()
    messages.success(request, 'Tarea marcada como completada.')
    return redirect('cunicultura:dashboard')

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario'])
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(TareaCunicultura, id=tarea_id)
    tarea.delete()
    messages.success(request, 'Tarea eliminada exitosamente.')
    return redirect('cunicultura:dashboard')

# Plan de Vacunación

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario', 'solo_vista', 'punto_blanco'])
def plan_vacunacion_list(request):
    planes = PlanVacunacion.objects.filter(is_active=True).order_by('fecha_programada')
    return render(request, 'cunicultura/plan_vacunacion_list.html', {'planes': planes})

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario'])
def plan_vacunacion_create(request):
    if request.method == 'POST':
        form = PlanVacunacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan de vacunación creado correctamente')
            return redirect('cunicultura:plan_vacunacion_list')
        else:
            messages.error(request, 'Revise los campos del formulario')
    else:
        form = PlanVacunacionForm()
    return render(request, 'cunicultura/plan_vacunacion_form.html', {'form': form, 'title': 'Crear Plan de Vacunación'})

@login_required
@role_required(['superusuario', 'admin_aves', 'veterinario'])
def plan_vacunacion_update(request, pk):
    plan = get_object_or_404(PlanVacunacion, pk=pk)
    if request.method == 'POST':
        form = PlanVacunacionForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan de vacunación actualizado correctamente')
            return redirect('cunicultura:plan_vacunacion_list')
        else:
            messages.error(request, 'Revise los campos del formulario')
    else:
        form = PlanVacunacionForm(instance=plan)
    return render(request, 'cunicultura/plan_vacunacion_form.html', {'form': form, 'title': 'Editar Plan de Vacunación'})

@login_required
@role_required(['superusuario', 'admin_cunicola', 'practicante_cunicola', 'veterinario'])
def plan_vacunacion_delete(request, pk):
    plan = get_object_or_404(PlanVacunacion, pk=pk)
    plan.is_active = False
    plan.save()
    messages.success(request, 'Plan de vacunación eliminado correctamente')
    return redirect('cunicultura:plan_vacunacion_list')

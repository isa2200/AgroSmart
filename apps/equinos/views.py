from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.usuarios.decorators import role_required
from .models import Tarea, Equino, RegistroDiario, TratamientoSalud, Novedad
from .forms import TareaForm, EquinoForm, RegistroDiarioForm

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario'])
def crear_equino(request):
    if request.method == 'POST':
        form = EquinoForm(request.POST, request.FILES)
        if form.is_valid():
            equino = form.save()
            messages.success(request, 'Equino registrado exitosamente.')
            return redirect('equinos:equino_list')
        else:
            messages.error(request, 'Error al registrar el equino. Verifique los datos.')
    else:
        form = EquinoForm()
    
    return render(request, 'equinos/equino_form.html', {'form': form})

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario', 'solo_vista'])
def equino_list(request):
    equinos = Equino.objects.filter(is_active=True).order_by('nombre')
    return render(request, 'equinos/equino_list.html', {'equinos': equinos})

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario', 'solo_vista'])
def equino_detail(request, equino_id):
    equino = get_object_or_404(Equino, id=equino_id)
    return render(request, 'equinos/equino_detail.html', {'equino': equino})

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario'])
def equino_update(request, equino_id):
    equino = get_object_or_404(Equino, id=equino_id)
    if request.method == 'POST':
        form = EquinoForm(request.POST, request.FILES, instance=equino)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equino actualizado exitosamente.')
            return redirect('equinos:equino_detail', equino_id=equino.id)
    else:
        form = EquinoForm(instance=equino)
    return render(request, 'equinos/equino_form.html', {'form': form, 'equino': equino})

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario'])
def crear_registro_diario(request):
    if request.method == 'POST':
        form = RegistroDiarioForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            if not registro.responsable:
                registro.responsable = request.user
            registro.save()
            messages.success(request, 'Bitácora diaria registrada exitosamente.')
            return redirect('equinos:dashboard')
        else:
            messages.error(request, 'Error al registrar la bitácora. Verifique los datos.')
    else:
        form = RegistroDiarioForm()
    
    return render(request, 'equinos/registro_diario_form.html', {'form': form})

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario'])
def crear_tarea(request):
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            if not tarea.responsable:
                tarea.responsable = request.user
            tarea.save()
            messages.success(request, 'Tarea creada exitosamente.')
            return redirect('equinos:dashboard')
        else:
            messages.error(request, 'Error al crear la tarea. Verifique los datos.')
    return redirect('equinos:dashboard')

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario'])
def completar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    tarea.estado = 'completada'
    tarea.save()
    messages.success(request, 'Tarea marcada como completada.')
    return redirect('equinos:dashboard')

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos'])
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    tarea.delete()
    messages.success(request, 'Tarea eliminada exitosamente.')
    return redirect('equinos:dashboard')

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario', 'solo_vista'])
def dashboard_equinos(request):
    """Vista principal del módulo de equinos: Dashboard General."""
    # Si es veterinario, redirigir directamente al plan de vacunación
    if request.user.perfilusuario.rol == 'veterinario':
        return redirect('equinos:plan_vacunacion_list')
        
    # Métricas
    total_equinos = Equino.objects.filter(is_active=True).count()


from .models import PlanVacunacion
from .forms import PlanVacunacionForm

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario', 'solo_vista', 'punto_blanco'])
def plan_vacunacion_list(request):
    planes = PlanVacunacion.objects.filter(is_active=True).order_by('fecha_programada')
    return render(request, 'equinos/plan_vacunacion_list.html', {'planes': planes})

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario'])
def plan_vacunacion_create(request):
    if request.method == 'POST':
        form = PlanVacunacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan de vacunación creado correctamente')
            return redirect('equinos:plan_vacunacion_list')
        else:
            messages.error(request, 'Revise los campos del formulario')
    else:
        form = PlanVacunacionForm()
    return render(request, 'equinos/plan_vacunacion_form.html', {'form': form, 'title': 'Crear Plan de Vacunación'})

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario'])
def plan_vacunacion_update(request, pk):
    plan = get_object_or_404(PlanVacunacion, pk=pk)
    if request.method == 'POST':
        form = PlanVacunacionForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan de vacunación actualizado correctamente')
            return redirect('equinos:plan_vacunacion_list')
        else:
            messages.error(request, 'Revise los campos del formulario')
    else:
        form = PlanVacunacionForm(instance=plan)
    return render(request, 'equinos/plan_vacunacion_form.html', {'form': form, 'title': 'Editar Plan de Vacunación'})

@login_required
@role_required(['superusuario', 'admin_equinos', 'practicante_equinos', 'veterinario'])
def plan_vacunacion_delete(request, pk):
    plan = get_object_or_404(PlanVacunacion, pk=pk)
    plan.is_active = False
    plan.save()
    messages.success(request, 'Plan de vacunación eliminado correctamente')
    return redirect('equinos:plan_vacunacion_list')

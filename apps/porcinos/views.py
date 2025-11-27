from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from apps.usuarios.decorators import role_required
from django.db.models import Sum
from .models import LotePorcino, BitacoraDiariaPorcinos
from .forms import LotePorcinoForm, BitacoraDiariaPorcinosForm



@login_required
@role_required(['superusuario', 'solo_vista'])
def dashboard(request):
    total_lotes = LotePorcino.objects.filter(is_active=True).count()
    total_cerdos = LotePorcino.objects.filter(is_active=True).aggregate(total=Sum('numero_cerdos_actual'))['total'] or 0
    context = {
        'total_lotes': total_lotes,
        'total_cerdos': total_cerdos,
    }
    return render(request, 'porcinos/dashboard.html', context)


@login_required
@role_required(['superusuario', 'solo_vista'])
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
@role_required(['superusuario'])
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
    return render(request, 'porcinos/lote_form.html', {'form': form})


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
        form = BitacoraDiariaPorcinosForm(request.POST)
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

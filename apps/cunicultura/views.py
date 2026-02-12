from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import InventarioConejos, PrecioConejo, LibroDiarioConejos
from .forms import InventarioConejosForm, LibroDiarioConejosForm

@login_required
def dashboard_cunicultura(request):
    """
    Dashboard principal del módulo de cunicultura.
    """
    # Manejar actualizaciones de precios vía AJAX
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            precio_id = data.get('id')
            campo = data.get('field')  # 'descripcion', 'edad_dias', o 'valor'
            nuevo_valor = data.get('value')
            
            if precio_id:
                precio = PrecioConejo.objects.get(id=precio_id)
                if campo == 'descripcion':
                    precio.descripcion = nuevo_valor
                elif campo == 'edad_dias':
                    precio.edad_dias = nuevo_valor
                elif campo == 'valor':
                    precio.valor = nuevo_valor if nuevo_valor else None
                precio.save()
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # Inicializar precios si no existen
    if not PrecioConejo.objects.exists():
        precios_iniciales = [
            (35, 42), (43, 49), (50, 56), (57, 63), (64, 70), 
            (71, 77), (78, 84), (85, 91), (92, 98), (99, 105),
            (106, 112), (113, 119), (120, 127), (127, 133), 
            (134, 140), (141, 147), (148, 154), (155, 161),
            (162, 168), (168, 175), (176, 182), (183, 189),
            (190, 196), (197, 203), (204, 210)
        ]
        
        for i, (min_d, max_d) in enumerate(precios_iniciales):
            PrecioConejo.objects.create(
                descripcion="Conejo en pie",
                edad_dias=f"{min_d} a {max_d}",
                orden=i
            )

    # Obtener precios para mostrar
    precios = PrecioConejo.objects.all()

    # Obtener el último registro de inventario para mostrar totales
    ultimo_inventario = InventarioConejos.objects.order_by('-fecha').first()
    
    # Valores por defecto si no hay registros
    total_conejos = 0
    gazapos = 0
    reproductores = 0
    levante_ceba = 0
    
    if ultimo_inventario:
        total_conejos = ultimo_inventario.total
        gazapos = ultimo_inventario.gazapos
        reproductores = ultimo_inventario.reproductores + ultimo_inventario.hembra_reemplazo + ultimo_inventario.hembra_no_lactando + ultimo_inventario.hembra_lactando
        levante_ceba = ultimo_inventario.macho_levante_ceba + ultimo_inventario.hembra_levante_ceba
        
    context = {
        'total_conejos': total_conejos,
        'gazapos': gazapos,
        'reproductores': reproductores,
        'levante_ceba': levante_ceba,
        'ultimo_inventario': ultimo_inventario,
        'precios': precios,
    }
    
    return render(request, 'cunicultura/dashboard.html', context)

@login_required
def inventario_permanente(request):
    """
    Vista para el Registro Inventario Permanente de Conejos
    """
    # Manejar actualizaciones inline vía AJAX
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            registro_id = data.get('id')
            campo = data.get('field')
            valor = data.get('value')
            
            if registro_id:
                registro = InventarioConejos.objects.get(id=registro_id)
                
                # Campos numéricos
                campos_numericos = [
                    'gazapos_vivos', 'gazapos_muertos', 'compra', 'venta', 'muerte',
                    'macho_levante_ceba', 'hembra_levante_ceba', 'reproductores',
                    'hembra_reemplazo', 'hembra_no_lactando', 'hembra_lactando', 'gazapos'
                ]
                
                if campo in campos_numericos:
                    setattr(registro, campo, int(valor) if valor else 0)
                elif campo == 'detalle':
                    registro.detalle = valor
                elif campo == 'madre_id':
                    registro.madre_id = valor
                
                registro.save()
                return JsonResponse({
                    'status': 'success', 
                    'new_total': registro.total
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    registros = InventarioConejos.objects.all().order_by('-fecha', '-id')
    
    if request.method == 'POST':
        form = InventarioConejosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cunicultura:inventario_permanente')
    else:
        form = InventarioConejosForm()
    
    context = {
        'registros': registros,
        'form': form,
    }
    return render(request, 'cunicultura/inventario_permanente.html', context)

@login_required
def libro_diario(request):
    """
    Vista para el Registro Libro Diario de Conejos
    """
    registros = LibroDiarioConejos.objects.all().order_by('-fecha', '-id')
    
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
    }
    return render(request, 'cunicultura/libro_diario.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, F
from datetime import datetime, timedelta

from apps.usuarios.decorators import punto_blanco_required, role_required
from .models import Pedido, DetallePedido, ConfiguracionPuntoBlanco
from .forms import PedidoForm, DetallePedidoFormSet, ConfiguracionPuntoBlancoForm
from apps.aves.models import InventarioHuevos, MovimientoHuevos, DetalleMovimientoHuevos


@login_required
@punto_blanco_required
def dashboard_punto_blanco(request):
    """Dashboard principal del punto blanco"""
    # Estadísticas del día
    hoy = timezone.now().date()
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy)
    
    estadisticas = {
        'pedidos_hoy': pedidos_hoy.count(),
        'pedidos_pendientes': pedidos_hoy.filter(estado='pendiente').count(),
        'pedidos_listos': pedidos_hoy.filter(estado='listo').count(),
        'ventas_hoy': pedidos_hoy.filter(estado='entregado').aggregate(
            total=Sum('total')
        )['total'] or 0,
    }
    
    # Pedidos recientes
    pedidos_recientes = Pedido.objects.order_by('-fecha_pedido')[:5]
    
    # Inventario de huevos completo
    inventarios_huevos = InventarioHuevos.objects.all().order_by('categoria')
    
    # Total de huevos disponibles
    total_huevos_disponibles = inventarios_huevos.aggregate(
        total=Sum('cantidad_actual')
    )['total'] or 0
    
    # Inventario con stock bajo
    inventarios_bajo_stock = inventarios_huevos.filter(
        cantidad_actual__lte=F('cantidad_minima')
    )
    
    # Movimientos recientes de huevos (últimos 10)
    # Corregido: removido 'cliente' del select_related ya que no es una relación ForeignKey
    movimientos_recientes = DetalleMovimientoHuevos.objects.select_related(
        'movimiento', 'movimiento__usuario_registro'
    ).order_by('-movimiento__fecha', '-movimiento__created_at')[:10]
    
    # Configuración del punto
    try:
        configuracion = ConfiguracionPuntoBlanco.objects.first()
    except ConfiguracionPuntoBlanco.DoesNotExist:
        configuracion = None
    
    # Calcular ingresos del día
    ingresos_hoy = pedidos_hoy.filter(estado='entregado').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    context = {
        'estadisticas': estadisticas,
        'pedidos_recientes': pedidos_recientes,
        'inventarios_huevos': inventarios_huevos,
        'total_huevos_disponibles': total_huevos_disponibles,
        'inventarios_bajo_stock': inventarios_bajo_stock,
        'movimientos_recientes': movimientos_recientes,
        'configuracion': configuracion,
        'pedidos_hoy': estadisticas['pedidos_hoy'],
        'ingresos_hoy': ingresos_hoy,
    }
    
    return render(request, 'punto_blanco_dashboard.html', context)


@login_required
@role_required(['punto_blanco'])
def lista_pedidos(request):
    """Lista de pedidos con filtros"""
    pedidos = Pedido.objects.order_by('-fecha_pedido')
    
    # Filtros
    estado = request.GET.get('estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    cliente = request.GET.get('cliente')
    
    if estado:
        pedidos = pedidos.filter(estado=estado)
    
    if fecha_desde:
        try:
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            pedidos = pedidos.filter(fecha_pedido__date__gte=fecha_desde)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            pedidos = pedidos.filter(fecha_pedido__date__lte=fecha_hasta)
        except ValueError:
            pass
    
    if cliente:
        pedidos = pedidos.filter(
            Q(cliente_nombre__icontains=cliente) |
            Q(cliente_telefono__icontains=cliente)
        )
    
    # Paginación
    paginator = Paginator(pedidos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filtros': {
            'estado': estado,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'cliente': cliente,
        }
    }
    
    return render(request, 'punto_blanco/lista_pedidos.html', context)


@login_required
@role_required(['punto_blanco'])
def crear_pedido(request):
    """Crear nuevo pedido"""
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        formset = DetallePedidoFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    pedido = form.save(commit=False)
                    pedido.creado_por = request.user
                    pedido.save()
                    
                    formset.instance = pedido
                    formset.save()
                    
                    # Calcular total
                    pedido.calcular_total()
                    
                    messages.success(request, f'Pedido #{pedido.numero_pedido} creado exitosamente.')
                    return redirect('punto_blanco:detalle_pedido', pk=pedido.pk)
                    
            except Exception as e:
                messages.error(request, f'Error al crear el pedido: {str(e)}')
    else:
        form = PedidoForm()
        formset = DetallePedidoFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'inventarios': InventarioHuevos.objects.filter(cantidad_actual__gt=0),
    }
    
    return render(request, 'punto_blanco/crear_pedido.html', context)


@login_required
@role_required(['punto_blanco'])
def detalle_pedido(request, pk):
    """Detalle de un pedido específico"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    context = {
        'pedido': pedido,
    }
    
    return render(request, 'punto_blanco/detalle_pedido.html', context)


@login_required
@role_required(['punto_blanco'])
def cambiar_estado_pedido(request, pk):
    """Cambiar estado de un pedido"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado in dict(Pedido.ESTADOS_CHOICES):
            try:
                with transaction.atomic():
                    pedido.estado = nuevo_estado
                    pedido.save()
                    
                    # Si se marca como entregado, actualizar inventario
                    if nuevo_estado == 'entregado':
                        pedido.actualizar_inventario()
                    
                    messages.success(request, f'Estado del pedido actualizado a {pedido.get_estado_display()}.')
            except Exception as e:
                messages.error(request, f'Error al actualizar el estado: {str(e)}')
        else:
            messages.error(request, 'Estado no válido.')
    
    return redirect('punto_blanco:detalle_pedido', pk=pk)


@login_required
@role_required(['punto_blanco'])
def inventario_punto_blanco(request):
    """Vista del inventario para punto blanco"""
    # Obtener todos los inventarios
    inventarios = InventarioHuevos.objects.all().order_by('categoria')
    
    # Estadísticas calculadas
    total_disponible = inventarios.aggregate(total=Sum('cantidad_actual'))['total'] or 0
    total_minimo = inventarios.aggregate(total=Sum('cantidad_minima'))['total'] or 0
    inventarios_criticos = inventarios.filter(cantidad_actual__lte=F('cantidad_minima')).count()
    
    context = {
        'inventarios': inventarios,
        'total_disponible': total_disponible,
        'total_minimo': total_minimo,
        'inventarios_criticos': inventarios_criticos,
        # Mantener las variables originales por compatibilidad
        'total_huevos': total_disponible,
        'inventarios_bajo': inventarios_criticos,
    }
    
    return render(request, 'punto_blanco_inventario.html', context)


@login_required
@role_required(['punto_blanco'])
def configuracion_punto_blanco(request):
    """Configuración del punto blanco"""
    try:
        configuracion = ConfiguracionPuntoBlanco.objects.first()
    except ConfiguracionPuntoBlanco.DoesNotExist:
        configuracion = None
    
    if request.method == 'POST':
        form = ConfiguracionPuntoBlancoForm(request.POST, instance=configuracion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada exitosamente')
            return redirect('punto_blanco:configuracion')
    else:
        form = ConfiguracionPuntoBlancoForm(instance=configuracion)
    
    context = {
        'form': form,
    }
    
    return render(request, 'punto_blanco/configuracion.html', context)


# API Views para AJAX
@login_required
@role_required(['punto_blanco'])
def api_inventario_info(request, inventario_id):
    """API para obtener información de inventario"""
    try:
        inventario = InventarioHuevos.objects.get(pk=inventario_id)
        data = {
            'categoria': inventario.categoria.nombre,
            'cantidad_actual': inventario.cantidad_actual,
            'precio_unitario': float(inventario.precio_unitario),
        }
        return JsonResponse(data)
    except InventarioHuevos.DoesNotExist:
        return JsonResponse({'error': 'Inventario no encontrado'}, status=404)
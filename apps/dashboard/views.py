from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
from apps.aves.models import LoteAves, BitacoraDiaria, InventarioAves
from apps.dashboard.models import AlertaSistema  # Usar el AlertaSistema del dashboard
from apps.usuarios.decorators import role_required
from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario
from django.views.decorators.http import require_POST
import json

@login_required
@role_required(['superusuario', 'admin_aves', 'admin_porcinos', 'admin_cunicola', 'admin_equinos', 
                'veterinario', 'solo_vista', 'punto_blanco',
                'practicante_aves', 'practicante_porcinos', 'practicante_cunicola', 'practicante_equinos'])
def dashboard_principal(request):
    """
    Vista principal del dashboard con métricas generales
    """
    # Métricas generales - Total Animales
    # Intentar obtener del último registro de InventarioAves
    ultimo_inventario = InventarioAves.objects.order_by('-fecha', '-created_at').first()
    
    if ultimo_inventario:
        total_aves = ultimo_inventario.total
    else:
        # Fallback: Sumar aves de lotes activos (levante y postura)
        total_aves = LoteAves.objects.filter(
            estado__in=['levante', 'postura']
        ).aggregate(
            total=Sum('numero_aves_actual')
        )['total'] or 0
    
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
    alertas_qs = AlertaSistema.objects.filter(
        created_at__gte=timezone.now().date() - timedelta(days=7),
        leida=False
    )
    total_alertas = alertas_qs.count()
    alertas = alertas_qs[:5]

    # Datos para las tarjetas de unidad
    all_unidades = [
        {
            'id': 'aves',
            'nombre': 'Unidad Avícola',
            'icon': 'fas fa-feather-alt',
            'color': 'success',
            'encargado_role': 'admin_aves',
            'practicante_role': 'practicante_aves',
            'url': 'aves:dashboard'
        },
        {
            'id': 'porcinos',
            'nombre': 'Unidad Porcinos',
            'icon': 'fas fa-piggy-bank',
            'color': 'warning',
            'encargado_role': 'admin_porcinos',
            'practicante_role': 'practicante_porcinos',
            'url': 'porcinos:dashboard'
        },
        {
            'id': 'cunicultura',
            'nombre': 'Unidad Cunícola',
            'icon': 'fas fa-carrot',
            'color': 'success',
            'encargado_role': 'admin_cunicola',
            'practicante_role': 'practicante_cunicola',
            'url': 'cunicultura:dashboard'
        },
        {
            'id': 'equinos',
            'nombre': 'Unidad Equinos',
            'icon': 'fas fa-horse-head',
            'color': 'primary',
            'encargado_role': 'admin_equinos',
            'practicante_role': 'practicante_equinos',
            'url': 'equinos:dashboard'
        },
        {
            'id': 'punto_blanco',
            'nombre': 'Punto de Venta',
            'icon': 'fas fa-store',
            'color': 'info',
            'encargado_role': 'punto_blanco',
            'practicante_role': 'punto_blanco', # Self-managed
            'url': 'punto_blanco:dashboard'
        }
    ]

    # Filtrar unidades según el rol del usuario
    user_rol = request.user.perfilusuario.rol
    unidades = []

    # Roles globales que ven todas las unidades
    roles_globales = ['superusuario', 'solo_vista']
    
    if user_rol in roles_globales:
        unidades = all_unidades
    elif user_rol == 'veterinario':
        # Veterinario ve todas las unidades productivas pero no Punto de Venta
        unidades = [u for u in all_unidades if u['id'] != 'punto_blanco']
    elif user_rol == 'punto_blanco':
        # Punto de Venta solo ve su unidad
        unidades = [u for u in all_unidades if u['id'] == 'punto_blanco']
    else:
        # Roles específicos de unidad
        for unidad in all_unidades:
            if user_rol == unidad['encargado_role'] or user_rol == unidad['practicante_role']:
                unidades.append(unidad)

    # Poblar datos de usuarios por unidad
    for unidad in unidades:
        encargados = PerfilUsuario.objects.filter(rol=unidad['encargado_role'])
        practicantes = PerfilUsuario.objects.filter(rol=unidad['practicante_role'])
        
        unidad['encargado'] = encargados.first().user if encargados.exists() else None
        unidad['num_practicantes'] = practicantes.count()
    
    context = {
        'total_aves': total_aves,
        'produccion_aves': total_produccion,
        'alertas': alertas,
        'total_alertas': total_alertas,
        'unidades': unidades,
    }
    
    return render(request, 'dashboard/principal.html', context)

@login_required
def obtener_usuarios_unidad(request):
    """API para obtener usuarios de una unidad específica"""
    unidad_id = request.GET.get('unidad')
    if not unidad_id:
        return JsonResponse({'error': 'Unidad no especificada'}, status=400)
        
    roles_map = {
        'aves': {'encargado': 'admin_aves', 'practicante': 'practicante_aves'},
        'porcinos': {'encargado': 'admin_porcinos', 'practicante': 'practicante_porcinos'},
        'cunicultura': {'encargado': 'admin_cunicola', 'practicante': 'practicante_cunicola'},
        'equinos': {'encargado': 'admin_equinos', 'practicante': 'practicante_equinos'},
    }
    
    roles = roles_map.get(unidad_id)
    if not roles:
        return JsonResponse({'error': 'Unidad inválida'}, status=400)
        
    encargados = PerfilUsuario.objects.filter(rol=roles['encargado']).select_related('user')
    practicantes = PerfilUsuario.objects.filter(rol=roles['practicante']).select_related('user')
    
    data = {
        'encargados': [{
            'id': p.user.id,
            'username': p.user.username,
            'nombre': p.user.get_full_name() or p.user.username,
            'email': p.user.email
        } for p in encargados],
        'practicantes': [{
            'id': p.user.id,
            'username': p.user.username,
            'nombre': p.user.get_full_name() or p.user.username,
            'email': p.user.email
        } for p in practicantes]
    }
    
    return JsonResponse(data)

@login_required
@require_POST
def agregar_usuario_unidad(request):
    """API para crear y asignar usuario a una unidad"""
    try:
        data = json.loads(request.body)
        unidad_id = data.get('unidad')
        tipo_usuario = data.get('tipo') # 'encargado' o 'practicante'
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email', '')
        
        if not all([unidad_id, tipo_usuario, username, password]):
            return JsonResponse({'error': 'Faltan datos requeridos'}, status=400)
            
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'El nombre de usuario ya existe'}, status=400)
            
        roles_map = {
            'aves': {'encargado': 'admin_aves', 'practicante': 'practicante_aves'},
            'porcinos': {'encargado': 'admin_porcinos', 'practicante': 'practicante_porcinos'},
            'cunicultura': {'encargado': 'admin_cunicola', 'practicante': 'practicante_cunicola'},
            'equinos': {'encargado': 'admin_equinos', 'practicante': 'practicante_equinos'},
        }
        
        roles = roles_map.get(unidad_id)
        if not roles:
            return JsonResponse({'error': 'Unidad inválida'}, status=400)
            
        rol_asignar = roles.get(tipo_usuario)
        if not rol_asignar:
            return JsonResponse({'error': 'Tipo de usuario inválido'}, status=400)
            
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Actualizar perfil (creado automáticamente por señal)
        try:
            perfil = user.perfilusuario
            perfil.rol = rol_asignar
            perfil.acceso_modulo_avicola = (unidad_id == 'aves')
            perfil.save()
        except PerfilUsuario.DoesNotExist:
            # Fallback por si la señal falla
            PerfilUsuario.objects.create(
                user=user,
                rol=rol_asignar,
                acceso_modulo_avicola=(unidad_id == 'aves')
            )
        
        return JsonResponse({'status': 'success', 'message': 'Usuario creado correctamente'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
            total_huevos=Sum(
                F('recoleccion_1') + F('recoleccion_2') + F('recoleccion_3')
            )
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
    ).values('linea_genetica').annotate(
        total_aves=Sum('numero_aves_actual')
    ).order_by('linea_genetica')
    
    # Preparar datos para el gráfico
    datos_inventario = []
    for lote in lotes_activos:
        datos_inventario.append({
            'linea': lote['linea_genetica'],
            'cantidad': lote['total_aves'] or 0
        })
    
    return JsonResponse({
        'inventario_animales': datos_inventario
    })
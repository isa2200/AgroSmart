from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from apps.usuarios.decorators import role_required

from .models import (
    LoteAves, ProduccionHuevos, CostosProduccion, 
    CalendarioVacunas, Vacunacion, Mortalidad
)
from .forms import (
    LoteAvesForm, ProduccionHuevosForm, CostosProduccionForm,
    VacunacionForm, MortalidadForm, FiltroProduccionForm
)

# ============= DASHBOARD PRINCIPAL MEJORADO =============
@login_required
def dashboard_aves(request):
    """Dashboard principal del módulo de aves con métricas completas"""
    hoy = timezone.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    hace_30_dias = hoy - timedelta(days=30)
    mes_actual = timezone.now().replace(day=1).date()
    
    # Obtener lotes activos
    lotes_activos = LoteAves.objects.filter(estado='activo').select_related('usuario')
    
    # 1. TOTAL AVES ACTIVAS
    total_aves_activas = lotes_activos.aggregate(total=Sum('cantidad_actual'))['total'] or 0
    
    # 2. PRODUCCIÓN DIARIA ACUMULADA (HOY)
    produccion_hoy = ProduccionHuevos.objects.filter(
        fecha=hoy,
        lote__in=lotes_activos
    ).aggregate(
        total_yumbos=Sum('yumbos'),
        total_extra=Sum('extra'),
        total_aa=Sum('aa'),
        total_a=Sum('a'),
        total_b=Sum('b'),
        total_c=Sum('c'),
        total_pipo=Sum('pipo'),
        total_sucios=Sum('sucios'),
        total_totiados=Sum('totiados'),
        total_yema=Sum('yema'),
        peso_promedio=Avg('peso_promedio_huevo'),
        aves_produccion=Sum('numero_aves_produccion')
    )
    
    # Calcular total huevos comerciales hoy
    huevos_comerciales_hoy = sum([
        produccion_hoy['total_yumbos'] or 0,
        produccion_hoy['total_extra'] or 0,
        produccion_hoy['total_aa'] or 0,
        produccion_hoy['total_a'] or 0,
        produccion_hoy['total_b'] or 0,
        produccion_hoy['total_c'] or 0
    ])
    
    # Total huevos incluyendo defectuosos
    total_huevos_hoy = huevos_comerciales_hoy + sum([
        produccion_hoy['total_pipo'] or 0,
        produccion_hoy['total_sucios'] or 0,
        produccion_hoy['total_totiados'] or 0,
        produccion_hoy['total_yema'] or 0
    ])
    
    # 3. % POSTURA PROMEDIO ÚLTIMOS 7 Y 30 DÍAS
    def calcular_postura_promedio(dias):
        fecha_inicio = hoy - timedelta(days=dias)
        producciones = ProduccionHuevos.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=hoy,
            lote__in=lotes_activos
        )
        
        if not producciones.exists():
            return 0
            
        total_huevos = 0
        total_aves_dia = 0
        
        for prod in producciones:
            huevos_dia = (prod.yumbos + prod.extra + prod.aa + prod.a + 
                         prod.b + prod.c + prod.pipo + prod.sucios + 
                         prod.totiados + prod.yema)
            total_huevos += huevos_dia
            total_aves_dia += prod.numero_aves_produccion
            
        if total_aves_dia > 0:
            return round((total_huevos / total_aves_dia) * 100, 2)
        return 0
    
    postura_7_dias = calcular_postura_promedio(7)
    postura_30_dias = calcular_postura_promedio(30)
    
    # 4. MORTALIDAD ACUMULADA (%)
    mortalidad_total = Mortalidad.objects.filter(
        lote__in=lotes_activos
    ).aggregate(total=Sum('cantidad_muertas'))['total'] or 0
    
    # Calcular cantidad inicial total
    cantidad_inicial_total = lotes_activos.aggregate(
        total=Sum('cantidad_aves')
    )['total'] or 0
    
    porcentaje_mortalidad = 0
    if cantidad_inicial_total > 0:
        porcentaje_mortalidad = round((mortalidad_total / cantidad_inicial_total) * 100, 2)
    
    # 5. GRAMOS AVE/DÍA (PROMEDIO ÚLTIMOS 30 DÍAS)
    gramos_ave_dia = ProduccionHuevos.objects.filter(
        fecha__gte=hace_30_dias,
        lote__in=lotes_activos
    ).aggregate(promedio=Avg('peso_promedio_huevo'))['promedio'] or 0
    
    if gramos_ave_dia:
        gramos_ave_dia = round(float(gramos_ave_dia), 2)
    
    # DATOS PARA GRÁFICAS
    # Producción últimos 30 días
    produccion_30_dias = []
    for i in range(30):
        fecha = hoy - timedelta(days=29-i)
        prod_dia = ProduccionHuevos.objects.filter(
            fecha=fecha,
            lote__in=lotes_activos
        ).aggregate(
            total=Sum('yumbos') + Sum('extra') + Sum('aa') + Sum('a') + 
                  Sum('b') + Sum('c')
        )['total'] or 0
        
        produccion_30_dias.append({
            'fecha': fecha.strftime('%d/%m'),
            'total': prod_dia
        })
    
    # Clasificación semanal de huevos (última semana)
    clasificacion_semanal = ProduccionHuevos.objects.filter(
        fecha__gte=hace_7_dias,
        lote__in=lotes_activos
    ).aggregate(
        yumbos=Sum('yumbos'),
        extra=Sum('extra'),
        aa=Sum('aa'),
        a=Sum('a'),
        b=Sum('b'),
        c=Sum('c'),
        pipo=Sum('pipo'),
        sucios=Sum('sucios'),
        totiados=Sum('totiados'),
        yema=Sum('yema')
    )
    
    # Mortalidad vs objetivo (objetivo: 5% anual)
    objetivo_mortalidad = 5.0
    
    # Ingresos vs Costos (mes actual)
    costos_mes = CostosProduccion.objects.filter(
        fecha__gte=mes_actual,
        lote__in=lotes_activos
    ).aggregate(
        total_costos=Sum('costos_fijos') + Sum('costos_variables') + 
                    Sum('gastos_administracion') + Sum('costo_alimento') + 
                    Sum('costo_mano_obra') + Sum('otros_costos'),
        total_ingresos=Sum('ingresos_venta_huevos') + Sum('ingresos_venta_aves') + 
                      Sum('otros_ingresos')
    )
    
    # Alertas de vacunación próximas
    proximas_vacunas = Vacunacion.objects.filter(
        fecha_programada__lte=hoy + timedelta(days=7),
        fecha_programada__gte=hoy,
        estado='pendiente'
    ).select_related('lote', 'calendario_vacuna')[:5]
    
    # Lotes con alertas sanitarias
    lotes_con_alertas = []
    for lote in lotes_activos:
        alertas = []
        
        # Alerta mortalidad alta (>2% semanal)
        mortalidad_semanal = Mortalidad.objects.filter(
            lote=lote,
            fecha__gte=hace_7_dias
        ).aggregate(total=Sum('cantidad_muertas'))['total'] or 0
        
        if lote.cantidad_actual > 0:
            porcentaje_semanal = (mortalidad_semanal / lote.cantidad_actual) * 100
            if porcentaje_semanal > 2:
                alertas.append(f'Mortalidad alta: {porcentaje_semanal:.1f}%')
        
        # Alerta postura baja (<70%)
        postura_lote = ProduccionHuevos.objects.filter(
            lote=lote,
            fecha__gte=hace_7_dias
        )
        
        if postura_lote.exists():
            avg_postura = postura_lote.aggregate(
                huevos=Avg('yumbos') + Avg('extra') + Avg('aa') + Avg('a') + 
                       Avg('b') + Avg('c'),
                aves=Avg('numero_aves_produccion')
            )
            
            if avg_postura['aves'] and avg_postura['huevos']:
                porcentaje_postura = (avg_postura['huevos'] / avg_postura['aves']) * 100
                if porcentaje_postura < 70:
                    alertas.append(f'Postura baja: {porcentaje_postura:.1f}%')
        
        if alertas:
            lotes_con_alertas.append({
                'lote': lote,
                'alertas': alertas
            })
    
    context = {
        # Indicadores principales
        'total_aves_activas': total_aves_activas,
        'huevos_comerciales_hoy': huevos_comerciales_hoy,
        'total_huevos_hoy': total_huevos_hoy,
        'postura_7_dias': postura_7_dias,
        'postura_30_dias': postura_30_dias,
        'porcentaje_mortalidad': porcentaje_mortalidad,
        'gramos_ave_dia': gramos_ave_dia,
        
        # Datos para gráficas
        'produccion_30_dias': produccion_30_dias,
        'clasificacion_semanal': clasificacion_semanal,
        'objetivo_mortalidad': objetivo_mortalidad,
        'costos_mes': costos_mes,
        
        # Datos adicionales
        'lotes_activos': lotes_activos,
        'proximas_vacunas': proximas_vacunas,
        'lotes_con_alertas': lotes_con_alertas,
        'fecha_actual': hoy.strftime('%d de %B de %Y'),
        'mes_actual': mes_actual.strftime('%B %Y')
    }
    
    return render(request, 'aves/dashboard.html', context)

# ============= GESTIÓN DE LOTES =============
@login_required
def lista_lotes(request):
    if request.user.groups.filter(name='solo_vista').exists():
        lotes = LoteAves.objects.filter(
            created_by=request.user
        ).order_by('-created_at')
    else:
        lotes = LoteAves.objects.all().order_by('-created_at')
    
    lotes = LoteAves.objects.all().order_by('-fecha_inicio')
    return render(request, 'aves/lotes/lista.html', {'lotes': lotes})

@login_required
def detalle_lote(request, lote_id):
    """Detalle completo de un lote específico"""
    lote = get_object_or_404(LoteAves, id=lote_id)
    
    # Producción reciente
    produccion_reciente = ProduccionHuevos.objects.filter(
        lote=lote
    ).order_by('-fecha')[:10]
    
    # Costos del mes
    mes_actual = timezone.now().replace(day=1)
    costos_mes = CostosProduccion.objects.filter(
        lote=lote,
        fecha__gte=mes_actual
    )
    
    # Vacunaciones
    vacunaciones = Vacunacion.objects.filter(
        lote=lote
    ).order_by('-fecha_aplicacion')[:5]
    
    # Mortalidad
    mortalidad_mes = Mortalidad.objects.filter(
        lote=lote,
        fecha__gte=mes_actual
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    # Indicadores
    indicadores = lote.calcular_indicadores()
    
    context = {
        'lote': lote,
        'produccion_reciente': produccion_reciente,
        'costos_mes': costos_mes,
        'vacunaciones': vacunaciones,
        'mortalidad_mes': mortalidad_mes,
        'indicadores': indicadores
    }
    
    return render(request, 'aves/lotes/detalle.html', context)

@login_required
def crear_lote(request):
    """Crear nuevo lote de aves"""
    if request.method == 'POST':
        form = LoteAvesForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.cantidad_actual = lote.cantidad_aves
            lote.save()
            messages.success(request, f'Lote {lote.codigo} creado exitosamente.')
            return redirect('aves:detalle_lote', lote_id=lote.id)
    else:
        form = LoteAvesForm()
    
    return render(request, 'aves/lotes/crear.html', {'form': form})

@login_required
def editar_lote(request, lote_id):
    """Editar lote existente"""
    lote = get_object_or_404(LoteAves, id=lote_id)
    
    if request.method == 'POST':
        form = LoteAvesForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lote {lote.codigo} actualizado exitosamente.')
            return redirect('aves:detalle_lote', lote_id=lote.id)
    else:
        form = LoteAvesForm(instance=lote)
    
    return render(request, 'aves/lotes/editar.html', {'form': form, 'lote': lote})

# ============= PRODUCCIÓN DE HUEVOS =============
@login_required
def lista_produccion(request):
    """Lista de registros de producción con filtros"""
    form = FiltroProduccionForm(request.GET or None)
    producciones = ProduccionHuevos.objects.select_related('lote').order_by('-fecha')
    
    if form.is_valid():
        if form.cleaned_data['lote']:
            producciones = producciones.filter(lote=form.cleaned_data['lote'])
        if form.cleaned_data['fecha_inicio']:
            producciones = producciones.filter(fecha__gte=form.cleaned_data['fecha_inicio'])
        if form.cleaned_data['fecha_fin']:
            producciones = producciones.filter(fecha__lte=form.cleaned_data['fecha_fin'])
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(producciones, 20)
    page = request.GET.get('page')
    producciones = paginator.get_page(page)
    
    context = {
        'producciones': producciones,
        'form': form
    }
    
    return render(request, 'aves/produccion/lista.html', context)

@login_required
def registrar_produccion(request):
    """Registrar nueva producción de huevos"""
    if request.method == 'POST':
        form = ProduccionHuevosForm(request.POST)
        if form.is_valid():
            produccion = form.save()
            messages.success(request, 'Producción registrada exitosamente.')
            return redirect('aves:lista_produccion')
    else:
        form = ProduccionHuevosForm()
    
    return render(request, 'aves/produccion/registrar.html', {'form': form})

@login_required
def editar_produccion(request, produccion_id):
    """Editar registro de producción"""
    produccion = get_object_or_404(ProduccionHuevos, id=produccion_id)
    
    if request.method == 'POST':
        form = ProduccionHuevosForm(request.POST, instance=produccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producción actualizada exitosamente.')
            return redirect('aves:lista_produccion')
    else:
        form = ProduccionHuevosForm(instance=produccion)
    
    return render(request, 'aves/produccion/editar.html', {'form': form, 'produccion': produccion})

# ============= COSTOS DE PRODUCCIÓN =============
@login_required
def lista_costos(request):
    """Lista de costos de producción"""
    costos = CostosProduccion.objects.select_related('lote').order_by('-fecha')
    return render(request, 'aves/costos/lista.html', {'costos': costos})

@login_required
def registrar_costos(request):
    """Registrar nuevos costos"""
    if request.method == 'POST':
        form = CostosProduccionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Costos registrados exitosamente.')
            return redirect('aves:lista_costos')
    else:
        form = CostosProduccionForm()
    
    return render(request, 'aves/costos/registrar.html', {'form': form})

# ============= VACUNACIÓN =============
@login_required
def calendario_vacunas(request):
    """Calendario de vacunación"""
    vacunas = CalendarioVacunas.objects.filter(is_active=True).order_by('dias_post_nacimiento')
    return render(request, 'aves/vacunas/calendario.html', {'vacunas': vacunas})

@login_required
def registrar_vacunacion(request):
    """Registrar aplicación de vacuna"""
    if request.method == 'POST':
        form = VacunacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vacunación registrada exitosamente.')
            return redirect('aves:calendario_vacunas')
    else:
        form = VacunacionForm()
    
    return render(request, 'aves/vacunas/registrar.html', {'form': form})

# ============= MORTALIDAD =============
@login_required
def lista_mortalidad(request):
    """Lista de registros de mortalidad"""
    mortalidades = Mortalidad.objects.select_related('lote').order_by('-fecha')
    return render(request, 'aves/mortalidad/lista.html', {'mortalidades': mortalidades})

@login_required
def registrar_mortalidad(request):
    """Registrar mortalidad"""
    if request.method == 'POST':
        form = MortalidadForm(request.POST)
        if form.is_valid():
            mortalidad = form.save()
            # Actualizar cantidad actual del lote
            lote = mortalidad.lote
            lote.cantidad_actual -= mortalidad.cantidad_muertas
            lote.save()
            messages.success(request, 'Mortalidad registrada exitosamente.')
            return redirect('aves:lista_mortalidad')
    else:
        form = MortalidadForm()
    
    return render(request, 'aves/mortalidad/registrar.html', {'form': form})

# ============= REPORTES Y GRÁFICAS =============
@login_required
def graficas_produccion(request):
    """Gráficas de producción para Chart.js"""
    lote_id = request.GET.get('lote_id')
    
    if lote_id:
        lote = get_object_or_404(LoteAves, id=lote_id)
        producciones = ProduccionHuevos.objects.filter(
            lote=lote
        ).order_by('fecha')[:30]  # Últimos 30 días
    else:
        producciones = ProduccionHuevos.objects.order_by('fecha')[:30]
    
    # Datos para gráficas
    fechas = [p.fecha.strftime('%Y-%m-%d') for p in producciones]
    huevos_buenos = [p.huevos_buenos for p in producciones]
    huevos_rotos = [p.huevos_rotos for p in producciones]
    porcentaje_postura = [float(p.porcentaje_postura) for p in producciones]
    
    data = {
        'fechas': fechas,
        'huevos_buenos': huevos_buenos,
        'huevos_rotos': huevos_rotos,
        'porcentaje_postura': porcentaje_postura
    }
    
    return JsonResponse(data)

@login_required
def reporte_rentabilidad(request):
    """Reporte de rentabilidad por lote"""
    lotes = LoteAves.objects.filter(estado='activo')
    reportes = []
    
    for lote in lotes:
        # Calcular indicadores básicos
        reportes.append({
            'lote': lote,
            'total_aves': lote.cantidad_actual,
            'mortalidad': lote.mortalidad_acumulada
        })
    
    return render(request, 'aves/reportes/rentabilidad.html', {'reportes': reportes})

@login_required
def alertas_sanitarias(request):
    """Sistema de alertas sanitarias"""
    alertas = []
    
    # Alertas de vacunación
    vacunas_pendientes = Vacunacion.objects.filter(
        fecha_programada__lte=timezone.now().date() + timedelta(days=3),
        fecha_programada__gte=timezone.now().date(),
        estado='pendiente'
    )
    
    for vacuna in vacunas_pendientes:
        alertas.append({
            'tipo': 'vacunacion',
            'mensaje': f'Vacuna {vacuna.calendario_vacuna.nombre_vacuna} programada para {vacuna.fecha_programada}',
            'lote': vacuna.lote,
            'urgencia': 'alta' if vacuna.fecha_programada <= timezone.now().date() else 'media'
        })
    
    # Alertas de mortalidad alta
    for lote in LoteAves.objects.filter(estado='activo'):
        mortalidad_semanal = Mortalidad.objects.filter(
            lote=lote,
            fecha__gte=timezone.now().date() - timedelta(days=7)
        ).aggregate(total=Sum('cantidad_muertas'))['total'] or 0
        
        if mortalidad_semanal > (lote.cantidad_actual * 0.02):  # Más del 2% semanal
            alertas.append({
                'tipo': 'mortalidad',
                'mensaje': f'Mortalidad alta en lote {lote.nombre_lote}: {mortalidad_semanal} aves',
                'lote': lote,
                'urgencia': 'alta'
            })
    
    return render(request, 'aves/alertas/sanitarias.html', {'alertas': alertas})

@login_required
@role_required(['superusuario', 'admin_aves'])  # agregado por corrección QA
def eliminar_lote(request, pk):
    """Eliminar lote de aves"""
    lote = get_object_or_404(LoteAves, pk=pk)
    if request.method == 'POST':
        codigo = lote.codigo
        lote.delete()
        messages.success(request, f'Lote {codigo} eliminado exitosamente.')
        return redirect('aves:lista_lotes')
    return render(request, 'aves/lotes/eliminar.html', {'lote': lote})

@login_required
@role_required(['superusuario', 'admin_aves'])
def crear_produccion(request):
    """Crear registro de producción"""
    if request.method == 'POST':
        form = ProduccionHuevosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producción registrada exitosamente.')
            return redirect('aves:lista_produccion')
    else:
        form = ProduccionHuevosForm()
    return render(request, 'aves/produccion/crear.html', {'form': form})

@login_required
@role_required(['superusuario', 'admin_aves'])
def eliminar_produccion(request, pk):
    """Eliminar registro de producción"""
    produccion = get_object_or_404(ProduccionHuevos, pk=pk)
    if request.method == 'POST':
        produccion.delete()
        messages.success(request, 'Registro de producción eliminado exitosamente.')
        return redirect('aves:lista_produccion')
    return render(request, 'aves/produccion/eliminar.html', {'produccion': produccion})

@login_required
def crear_costo(request):
    """Crear registro de costo"""
    if request.method == 'POST':
        form = CostosProduccionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Costo registrado exitosamente.')
            return redirect('aves:lista_costos')
    else:
        form = CostosProduccionForm()
    return render(request, 'aves/costos/crear.html', {'form': form})

@login_required
def editar_costo(request, pk):
    """Editar registro de costo"""
    costo = get_object_or_404(CostosProduccion, pk=pk)
    if request.method == 'POST':
        form = CostosProduccionForm(request.POST, instance=costo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Costo actualizado exitosamente.')
            return redirect('aves:lista_costos')
    else:
        form = CostosProduccionForm(instance=costo)
    return render(request, 'aves/costos/editar.html', {'form': form, 'costo': costo})

@login_required
def eliminar_costo(request, pk):
    """Eliminar registro de costo"""
    costo = get_object_or_404(CostosProduccion, pk=pk)
    if request.method == 'POST':
        costo.delete()
        messages.success(request, 'Costo eliminado exitosamente.')
        return redirect('aves:lista_costos')
    return render(request, 'aves/costos/eliminar.html', {'costo': costo})

@login_required
def lista_vacunacion(request):
    """Lista de vacunaciones aplicadas"""
    vacunaciones = Vacunacion.objects.select_related('lote').order_by('-fecha_aplicacion')
    return render(request, 'aves/vacunacion/lista.html', {'vacunaciones': vacunaciones})

@login_required
def crear_vacunacion(request):
    """Crear registro de vacunación"""
    if request.method == 'POST':
        form = VacunacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vacunación registrada exitosamente.')
            return redirect('aves:lista_vacunacion')
    else:
        form = VacunacionForm()
    return render(request, 'aves/vacunacion/crear.html', {'form': form})

@login_required
def editar_vacunacion(request, pk):
    """Editar registro de vacunación"""
    vacunacion = get_object_or_404(Vacunacion, pk=pk)
    if request.method == 'POST':
        form = VacunacionForm(request.POST, instance=vacunacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vacunación actualizada exitosamente.')
            return redirect('aves:lista_vacunacion')
    else:
        form = VacunacionForm(instance=vacunacion)
    return render(request, 'aves/vacunacion/editar.html', {'form': form, 'vacunacion': vacunacion})

@login_required
def eliminar_vacunacion(request, pk):
    """Eliminar registro de vacunación"""
    vacunacion = get_object_or_404(Vacunacion, pk=pk)
    if request.method == 'POST':
        vacunacion.delete()
        messages.success(request, 'Vacunación eliminada exitosamente.')
        return redirect('aves:lista_vacunacion')
    return render(request, 'aves/vacunacion/eliminar.html', {'vacunacion': vacunacion})

@login_required
def crear_mortalidad(request):
    """Crear registro de mortalidad"""
    if request.method == 'POST':
        form = MortalidadForm(request.POST)
        if form.is_valid():
            mortalidad = form.save()
            # Actualizar cantidad actual del lote
            lote = mortalidad.lote
            lote.cantidad_actual -= mortalidad.cantidad_muertas
            lote.save()
            messages.success(request, 'Mortalidad registrada exitosamente.')
            return redirect('aves:lista_mortalidad')
    else:
        form = MortalidadForm()
    return render(request, 'aves/mortalidad/crear.html', {'form': form})

@login_required
def editar_mortalidad(request, pk):
    """Editar registro de mortalidad"""
    mortalidad = get_object_or_404(Mortalidad, pk=pk)
    cantidad_anterior = mortalidad.cantidad_muertas
    
    if request.method == 'POST':
        form = MortalidadForm(request.POST, instance=mortalidad)
        if form.is_valid():
            mortalidad_nueva = form.save()
            # Ajustar cantidad del lote
            lote = mortalidad_nueva.lote
            diferencia = mortalidad_nueva.cantidad - cantidad_anterior
            lote.cantidad_actual -= diferencia
            lote.save()
            messages.success(request, 'Mortalidad actualizada exitosamente.')
            return redirect('aves:lista_mortalidad')
    else:
        form = MortalidadForm(instance=mortalidad)
    return render(request, 'aves/mortalidad/editar.html', {'form': form, 'mortalidad': mortalidad})

@login_required
def eliminar_mortalidad(request, pk):
    """Eliminar registro de mortalidad"""
    mortalidad = get_object_or_404(Mortalidad, pk=pk)
    if request.method == 'POST':
        # Restaurar cantidad al lote
        lote = mortalidad.lote
        lote.cantidad_actual += mortalidad.cantidad_muertas
        lote.save()
        mortalidad.delete()
        messages.success(request, 'Registro de mortalidad eliminado exitosamente.')
        return redirect('aves:lista_mortalidad')
    return render(request, 'aves/mortalidad/eliminar.html', {'mortalidad': mortalidad})

# ============= APIs PARA GRÁFICOS =============
@login_required
def api_produccion_semanal(request):
    """API para datos de producción semanal"""
    lote_id = request.GET.get('lote_id')
    
    # Obtener datos de las últimas 12 semanas
    fecha_inicio = timezone.now().date() - timedelta(weeks=12)
    
    if lote_id:
        producciones = ProduccionHuevos.objects.filter(
            lote_id=lote_id,
            fecha__gte=fecha_inicio
        )
    else:
        producciones = ProduccionHuevos.objects.filter(
            fecha__gte=fecha_inicio
        )
    
    # Agrupar por semana
    from django.db.models import Week
    datos_semanales = producciones.extra({
        'semana': "strftime('%%Y-%%W', fecha)"
    }).values('semana').annotate(
        total_huevos=Sum('huevos_buenos'),
        total_rotos=Sum('huevos_rotos')
    ).order_by('semana')
    
    semanas = [item['semana'] for item in datos_semanales]
    huevos = [item['total_huevos'] or 0 for item in datos_semanales]
    rotos = [item['total_rotos'] or 0 for item in datos_semanales]
    
    return JsonResponse({
        'semanas': semanas,
        'huevos_buenos': huevos,
        'huevos_rotos': rotos
    })

@login_required
def api_costos_mensuales(request):
    """API para datos de costos mensuales"""
    lote_id = request.GET.get('lote_id')
    
    # Obtener datos de los últimos 6 meses
    fecha_inicio = timezone.now().date() - timedelta(days=180)
    
    if lote_id:
        costos = CostosProduccion.objects.filter(
            lote_id=lote_id,
            fecha__gte=fecha_inicio
        )
    else:
        costos = CostosProduccion.objects.filter(
            fecha__gte=fecha_inicio
        )
    
    # Agrupar por mes
    datos_mensuales = costos.extra({
        'mes': "strftime('%%Y-%%m', fecha)"
    }).values('mes').annotate(
        total_alimento=Sum('costo_alimento'),
        total_medicamentos=Sum('costo_medicamentos'),
        total_otros=Sum('otros_costos')
    ).order_by('mes')
    
    meses = [item['mes'] for item in datos_mensuales]
    alimento = [float(item['total_alimento'] or 0) for item in datos_mensuales]
    medicamentos = [float(item['total_medicamentos'] or 0) for item in datos_mensuales]
    otros = [float(item['total_otros'] or 0) for item in datos_mensuales]
    
    return JsonResponse({
        'meses': meses,
        'alimento': alimento,
        'medicamentos': medicamentos,
        'otros': otros
    })

@login_required
def api_indicadores(request):
    lote_id = request.GET.get('lote_id')
    
    if lote_id:
        lote = get_object_or_404(LoteAves, id=lote_id)
        indicadores = {
            'total_aves': lote.cantidad_actual,
            'mortalidad': lote.mortalidad_acumulada,
            'edad_semanas': lote.edad_semanas
        }
    else:
        # Indicadores generales de todos los lotes activos
        lotes_activos = LoteAves.objects.filter(estado='activo')
        total_aves = sum(lote.cantidad_actual for lote in lotes_activos)
        
        # Producción del mes
        mes_actual = timezone.now().replace(day=1)
        produccion_mes = ProduccionHuevos.objects.filter(
            fecha__gte=mes_actual,
            lote__in=lotes_activos
        ).aggregate(
            total_huevos=Sum('yumbos') + Sum('extra') + Sum('aa') + Sum('a') + Sum('b') + Sum('c'),
            total_rotos=Sum('totiados')
        )
        
        indicadores = {
            'total_aves': total_aves,
            'produccion_mes': produccion_mes['total_huevos'] or 0,
            'huevos_rotos_mes': produccion_mes['total_rotos'] or 0,
            'porcentaje_postura': round((produccion_mes['total_huevos'] or 0) / total_aves * 100, 2) if total_aves > 0 else 0
        }
    
    return JsonResponse(indicadores)

# PRODUCCIÓN DE HUEVOS
def validar_produccion_huevos(produccion):
    # Fecha dentro del rango del lote
    if produccion.fecha < produccion.lote.fecha_inicio:
        raise ValidationError("Fecha no puede ser anterior al inicio del lote")
    
    # Aves en producción ≤ aves actuales del lote
    if produccion.numero_aves_produccion > produccion.lote.cantidad_actual:
        raise ValidationError("Aves en producción exceden aves actuales del lote")
    
    # Peso promedio dentro de rangos esperados (45-80g)
    if not (45 <= produccion.peso_promedio_huevo <= 80):
        raise ValidationError("Peso promedio fuera de rango esperado (45-80g)")
    
    # Porcentaje de postura realista (0-120%)
    porcentaje = (produccion.total_huevos / produccion.numero_aves_produccion) * 100
    if porcentaje > 120:
        raise ValidationError("Porcentaje de postura excede límite realista (120%)")

# CLASIFICACIÓN DE HUEVOS
def validar_clasificacion_huevos(clasificacion):
    total_clasificados = sum([
        clasificacion.yumbos, clasificacion.extra, clasificacion.aa,
        clasificacion.a, clasificacion.b, clasificacion.c,
        clasificacion.pipo, clasificacion.sucios, 
        clasificacion.totiados, clasificacion.yema
    ])
    
    if total_clasificados != clasificacion.produccion.total_huevos:
        raise ValidationError(
            f"Total clasificados ({total_clasificados}) debe igual total producido "
            f"({clasificacion.produccion.total_huevos})"
        )

# MORTALIDAD
def validar_mortalidad(mortalidad):
    # No puede exceder aves actuales
    if mortalidad.cantidad_muertas > mortalidad.lote.cantidad_actual:
        raise ValidationError("Mortalidad excede aves actuales del lote")
    
    # Mortalidad diaria máxima 10%
    porcentaje_diario = (mortalidad.cantidad_muertas / mortalidad.lote.cantidad_actual) * 100
    if porcentaje_diario > 10:
        raise ValidationError("Mortalidad diaria excede 10% (revisar datos)")

# COSTOS
def validar_costos_produccion(costos):
    # Costos no pueden ser negativos
    campos_costo = ['costos_fijos', 'costos_variables', 'costo_alimento', 'costo_mano_obra']
    for campo in campos_costo:
        if getattr(costos, campo) < 0:
            raise ValidationError(f"{campo} no puede ser negativo")
    
    # Costo por huevo realista (0.05 - 2.00 USD)
    if costos.total_costos > 0:
        produccion_periodo = costos.lote.producciones.filter(
            fecha__range=[costos.fecha - timedelta(days=7), costos.fecha]
        ).aggregate(total=Sum('total_huevos'))['total'] or 1
        
        costo_por_huevo = costos.total_costos / produccion_periodo
        if not (0.05 <= costo_por_huevo <= 2.00):
            raise ValidationError(f"Costo por huevo fuera de rango esperado: ${costo_por_huevo:.3f}")
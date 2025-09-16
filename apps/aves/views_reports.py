"""
Vistas para el sistema de reportes del módulo avícola
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import json

from apps.usuarios.decorators import requiere_permiso_avicola
from .models import LoteAves, Galpon, LineaGenetica
from .reports import ReporteAvicola, ReporteComparativo, obtener_datos_dashboard

@login_required
@requiere_permiso_avicola
def dashboard_reportes(request):
    """
    Dashboard principal de reportes avícolas
    """
    datos_dashboard = obtener_datos_dashboard()
    
    # Obtener lotes activos para filtros
    lotes_activos = LoteAves.objects.filter(estado='activo').select_related('galpon', 'linea_genetica')
    galpones = Galpon.objects.filter(activo=True)
    
    context = {
        'datos_dashboard': datos_dashboard,
        'lotes_activos': lotes_activos,
        'galpones': galpones,
        'titulo': 'Dashboard de Reportes Avícolas'
    }
    
    return render(request, 'aves/reportes/dashboard.html', context)

@login_required
@requiere_permiso_avicola
def generar_reporte_produccion(request):
    """
    Genera reportes de producción en diferentes formatos
    """
    if request.method == 'POST':
        try:
            # Obtener parámetros del formulario
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            lote_id = request.POST.get('lote_id')
            galpon_id = request.POST.get('galpon_id')
            formato = request.POST.get('formato', 'pdf')
            
            # Convertir fechas
            parametros = {}
            if fecha_inicio:
                parametros['fecha_inicio'] = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if fecha_fin:
                parametros['fecha_fin'] = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            if lote_id:
                parametros['lote_id'] = int(lote_id)
            if galpon_id:
                parametros['galpon_id'] = int(galpon_id)
            
            # Crear instancia del reporte
            reporte = ReporteAvicola(parametros)
            
            # Generar según formato
            if formato == 'pdf':
                return reporte.generar_pdf_produccion()
            elif formato == 'excel':
                return reporte.generar_excel_produccion()
            elif formato == 'csv':
                return reporte.generar_csv_produccion()
            else:
                messages.error(request, 'Formato de reporte no válido')
                
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {str(e)}')
    
    # Si es GET o hay error, mostrar formulario
    lotes_activos = LoteAves.objects.filter(estado='activo').select_related('galpon')
    galpones = Galpon.objects.filter(activo=True)
    
    context = {
        'lotes_activos': lotes_activos,
        'galpones': galpones,
        'titulo': 'Generar Reporte de Producción'
    }
    
    return render(request, 'aves/reportes/generar_produccion.html', context)

@login_required
@requiere_permiso_avicola
def reporte_comparativo_lotes(request):
    """
    Genera reportes comparativos entre lotes
    """
    if request.method == 'POST':
        try:
            lotes_ids = request.POST.getlist('lotes_ids')
            fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            formato = request.POST.get('formato', 'excel')
            
            if not lotes_ids:
                messages.error(request, 'Debe seleccionar al menos un lote')
                return render(request, 'aves/reportes/comparativo_lotes.html', {
                    'lotes_activos': LoteAves.objects.filter(estado='activo'),
                    'titulo': 'Reporte Comparativo de Lotes'
                })
            
            # Generar reporte comparativo
            reporte_comp = ReporteComparativo()
            datos_comparacion = reporte_comp.comparar_lotes(lotes_ids, fecha_inicio, fecha_fin)
            
            if formato == 'json':
                return JsonResponse({'datos': datos_comparacion})
            elif formato == 'excel':
                return generar_excel_comparativo_lotes(datos_comparacion, fecha_inicio, fecha_fin)
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte comparativo: {str(e)}')
    
    lotes_activos = LoteAves.objects.filter(estado='activo').select_related('galpon', 'linea_genetica')
    
    context = {
        'lotes_activos': lotes_activos,
        'titulo': 'Reporte Comparativo de Lotes'
    }
    
    return render(request, 'aves/reportes/comparativo_lotes.html', context)

@login_required
@requiere_permiso_avicola
def reporte_comparativo_periodos(request):
    """
    Genera reportes comparativos de períodos para un lote
    """
    if request.method == 'POST':
        try:
            lote_id = request.POST.get('lote_id')
            periodos_data = json.loads(request.POST.get('periodos', '[]'))
            formato = request.POST.get('formato', 'excel')
            
            if not lote_id or not periodos_data:
                messages.error(request, 'Debe seleccionar un lote y definir períodos')
                return render(request, 'aves/reportes/comparativo_periodos.html', {
                    'lotes_activos': LoteAves.objects.filter(estado='activo'),
                    'titulo': 'Reporte Comparativo de Períodos'
                })
            
            # Convertir fechas de períodos
            periodos = []
            for periodo in periodos_data:
                periodos.append({
                    'nombre': periodo['nombre'],
                    'fecha_inicio': datetime.strptime(periodo['fecha_inicio'], '%Y-%m-%d').date(),
                    'fecha_fin': datetime.strptime(periodo['fecha_fin'], '%Y-%m-%d').date()
                })
            
            # Generar reporte comparativo
            reporte_comp = ReporteComparativo()
            datos_comparacion = reporte_comp.comparar_periodos(lote_id, periodos)
            
            if formato == 'json':
                return JsonResponse({'datos': datos_comparacion})
            elif formato == 'excel':
                return generar_excel_comparativo_periodos(datos_comparacion, lote_id)
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte comparativo: {str(e)}')
    
    lotes_activos = LoteAves.objects.filter(estado='activo').select_related('galpon')
    
    context = {
        'lotes_activos': lotes_activos,
        'titulo': 'Reporte Comparativo de Períodos'
    }
    
    return render(request, 'aves/reportes/comparativo_periodos.html', context)

@login_required
@requiere_permiso_avicola
@require_http_methods(["GET"])
def api_datos_dashboard(request):
    """
    API para obtener datos del dashboard en tiempo real
    """
    try:
        datos = obtener_datos_dashboard()
        return JsonResponse({'success': True, 'datos': datos})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@requiere_permiso_avicola
@require_http_methods(["GET"])
def api_datos_produccion_lote(request, lote_id):
    """
    API para obtener datos de producción de un lote específico
    """
    try:
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        parametros = {'lote_id': lote_id}
        if fecha_inicio:
            parametros['fecha_inicio'] = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        if fecha_fin:
            parametros['fecha_fin'] = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        reporte = ReporteAvicola(parametros)
        datos_produccion = reporte.obtener_datos_produccion_diaria()
        resumen = reporte.obtener_resumen_produccion()
        
        # Convertir fechas a string para JSON
        for dato in datos_produccion:
            dato['fecha'] = dato['fecha'].strftime('%Y-%m-%d')
        
        return JsonResponse({
            'success': True,
            'datos_produccion': datos_produccion,
            'resumen': resumen
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@requiere_permiso_avicola
def exportar_datos_completos(request):
    """
    Exporta todos los datos del módulo avícola
    """
    if request.method == 'POST':
        try:
            formato = request.POST.get('formato', 'excel')
            incluir_historicos = request.POST.get('incluir_historicos') == 'on'
            
            if formato == 'excel':
                return generar_excel_datos_completos(incluir_historicos)
            elif formato == 'csv':
                return generar_csv_datos_completos(incluir_historicos)
                
        except Exception as e:
            messages.error(request, f'Error al exportar datos: {str(e)}')
    
    context = {
        'titulo': 'Exportar Datos Completos'
    }
    
    return render(request, 'aves/reportes/exportar_completo.html', context)

@login_required
@requiere_permiso_avicola
def reporte_salud_vacunacion(request):
    """
    Genera reportes de salud y vacunación
    """
    if request.method == 'POST':
        try:
            fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            lote_id = request.POST.get('lote_id')
            formato = request.POST.get('formato', 'pdf')
            
            parametros = {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
            if lote_id:
                parametros['lote_id'] = int(lote_id)
            
            reporte = ReporteAvicola(parametros)
            
            if formato == 'pdf':
                return reporte.generar_pdf_salud()
            elif formato == 'excel':
                return reporte.generar_excel_salud()
                
        except Exception as e:
            messages.error(request, f'Error al generar reporte de salud: {str(e)}')
    
    lotes_activos = LoteAves.objects.filter(estado='activo').select_related('galpon')
    
    context = {
        'lotes_activos': lotes_activos,
        'titulo': 'Reporte de Salud y Vacunación'
    }
    
    return render(request, 'aves/reportes/salud_vacunacion.html', context)

@login_required
@requiere_permiso_avicola
def reporte_consumo_alimento(request):
    """
    Genera reportes de consumo de alimento
    """
    if request.method == 'POST':
        try:
            fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d').date()
            lote_id = request.POST.get('lote_id')
            formato = request.POST.get('formato', 'excel')
            
            parametros = {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            }
            if lote_id:
                parametros['lote_id'] = int(lote_id)
            
            reporte = ReporteAvicola(parametros)
            
            if formato == 'excel':
                return reporte.generar_excel_consumo_alimento()
            elif formato == 'pdf':
                return reporte.generar_pdf_consumo_alimento()
                
        except Exception as e:
            messages.error(request, f'Error al generar reporte de consumo: {str(e)}')
    
    lotes_activos = LoteAves.objects.filter(estado='activo').select_related('galpon')
    
    context = {
        'lotes_activos': lotes_activos,
        'titulo': 'Reporte de Consumo de Alimento'
    }
    
    return render(request, 'aves/reportes/consumo_alimento.html', context)

def generar_excel_comparativo_lotes(datos_comparacion, fecha_inicio, fecha_fin):
    """
    Genera Excel para reporte comparativo de lotes
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        from openpyxl.chart import BarChart, Reference
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Comparativo Lotes"
        
        # Título
        ws['A1'] = "Reporte Comparativo de Lotes"
        ws['A1'].font = Font(size=16, bold=True)
        ws.merge_cells('A1:L1')
        
        # Información del reporte
        ws['A3'] = f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
        ws['A4'] = f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Encabezados
        encabezados = [
            'Código Lote', 'Nombre Lote', 'Galpón', 'Línea Genética', 'Cantidad Aves',
            'Total Huevos', 'Huevos Buenos', 'Huevos Rotos', 'Huevos Sucios',
            'Mortalidad', '% Postura Promedio', 'Huevos/Ave/Día'
        ]
        
        for i, encabezado in enumerate(encabezados, start=1):
            celda = ws.cell(row=6, column=i, value=encabezado)
            celda.font = Font(bold=True)
            celda.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Datos
        for i, dato in enumerate(datos_comparacion, start=7):
            ws.cell(row=i, column=1, value=dato['lote_codigo'])
            ws.cell(row=i, column=2, value=dato['lote_nombre'])
            ws.cell(row=i, column=3, value=dato['galpon'])
            ws.cell(row=i, column=4, value=dato['linea_genetica'])
            ws.cell(row=i, column=5, value=dato['cantidad_aves'])
            ws.cell(row=i, column=6, value=dato['total_huevos'])
            ws.cell(row=i, column=7, value=dato['huevos_buenos'])
            ws.cell(row=i, column=8, value=dato['huevos_rotos'])
            ws.cell(row=i, column=9, value=dato['huevos_sucios'])
            ws.cell(row=i, column=10, value=dato['total_mortalidad'])
            ws.cell(row=i, column=11, value=dato['promedio_postura'])
            ws.cell(row=i, column=12, value=dato['huevos_por_ave_dia'])
        
        # Crear gráfico comparativo
        chart = BarChart()
        chart.title = "Comparativo de Producción por Lote"
        chart.style = 10
        chart.x_axis.title = 'Lotes'
        chart.y_axis.title = 'Total Huevos'
        
        data = Reference(ws, min_col=6, min_row=6, max_col=6, max_row=len(datos_comparacion)+6)
        cats = Reference(ws, min_col=1, min_row=7, max_row=len(datos_comparacion)+6)
        
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        ws.add_chart(chart, "N6")
        
        # Guardar en buffer
        import io
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="comparativo_lotes.xlsx"'
        return response
        
    except ImportError:
        raise ImportError("openpyxl no está disponible")

def generar_excel_comparativo_periodos(datos_comparacion, lote_id):
    """
    Genera Excel para reporte comparativo de períodos
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
        from openpyxl.chart import LineChart, Reference
        
        lote = get_object_or_404(LoteAves, id=lote_id)
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Comparativo Períodos"
        
        # Título
        ws['A1'] = f"Reporte Comparativo de Períodos - Lote {lote.codigo}"
        ws['A1'].font = Font(size=16, bold=True)
        ws.merge_cells('A1:K1')
        
        # Encabezados
        encabezados = [
            'Período', 'Fecha Inicio', 'Fecha Fin', 'Total Huevos', 'Huevos Buenos',
            'Huevos Rotos', 'Huevos Sucios', 'Mortalidad', 'Temp. Promedio',
            'Humedad Promedio', 'Promedio Huevos/Día'
        ]
        
        for i, encabezado in enumerate(encabezados, start=1):
            celda = ws.cell(row=3, column=i, value=encabezado)
            celda.font = Font(bold=True)
            celda.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Datos
        for i, dato in enumerate(datos_comparacion, start=4):
            ws.cell(row=i, column=1, value=dato['periodo'])
            ws.cell(row=i, column=2, value=dato['fecha_inicio'])
            ws.cell(row=i, column=3, value=dato['fecha_fin'])
            ws.cell(row=i, column=4, value=dato['total_huevos'])
            ws.cell(row=i, column=5, value=dato['huevos_buenos'])
            ws.cell(row=i, column=6, value=dato['huevos_rotos'])
            ws.cell(row=i, column=7, value=dato['huevos_sucios'])
            ws.cell(row=i, column=8, value=dato['total_mortalidad'])
            ws.cell(row=i, column=9, value=dato['promedio_temperatura'])
            ws.cell(row=i, column=10, value=dato['promedio_humedad'])
            ws.cell(row=i, column=11, value=dato['promedio_huevos_dia'])
        
        # Crear gráfico de evolución
        chart = LineChart()
        chart.title = "Evolución de Producción por Período"
        chart.style = 13
        chart.x_axis.title = 'Períodos'
        chart.y_axis.title = 'Promedio Huevos/Día'
        
        data = Reference(ws, min_col=11, min_row=3, max_col=11, max_row=len(datos_comparacion)+3)
        cats = Reference(ws, min_col=1, min_row=4, max_row=len(datos_comparacion)+3)
        
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        ws.add_chart(chart, "M3")
        
        # Guardar en buffer
        import io
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="comparativo_periodos_lote_{lote.codigo}.xlsx"'
        return response
        
    except ImportError:
        raise ImportError("openpyxl no está disponible")

def generar_excel_datos_completos(incluir_historicos=False):
    """
    Genera Excel con todos los datos del módulo avícola
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
        
        wb = openpyxl.Workbook()
        
        # Hoja 1: Lotes
        ws_lotes = wb.active
        ws_lotes.title = "Lotes"
        
        encabezados_lotes = ['Código', 'Nombre', 'Galpón', 'Línea Genética', 'Fecha Ingreso', 'Cantidad Inicial', 'Cantidad Actual', 'Estado']
        for i, encabezado in enumerate(encabezados_lotes, start=1):
            celda = ws_lotes.cell(row=1, column=i, value=encabezado)
            celda.font = Font(bold=True)
            celda.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        filtro_lotes = {} if incluir_historicos else {'estado': 'activo'}
        lotes = LoteAves.objects.filter(**filtro_lotes).select_related('galpon', 'linea_genetica')
        
        for i, lote in enumerate(lotes, start=2):
            ws_lotes.cell(row=i, column=1, value=lote.codigo)
            ws_lotes.cell(row=i, column=2, value=lote.nombre_lote)
            ws_lotes.cell(row=i, column=3, value=lote.galpon.nombre)
            ws_lotes.cell(row=i, column=4, value=lote.linea_genetica.nombre)
            ws_lotes.cell(row=i, column=5, value=lote.fecha_ingreso)
            ws_lotes.cell(row=i, column=6, value=lote.cantidad_inicial)
            ws_lotes.cell(row=i, column=7, value=lote.cantidad_actual)
            ws_lotes.cell(row=i, column=8, value=lote.get_estado_display())
        
        # Hoja 2: Producción (últimos 90 días o todos si incluir_historicos)
        ws_produccion = wb.create_sheet("Producción")
        
        from .reports import ReporteAvicola
        parametros = {}
        if not incluir_historicos:
            parametros['fecha_inicio'] = timezone.now().date() - timedelta(days=90)
        
        reporte = ReporteAvicola(parametros)
        datos_produccion = reporte.obtener_datos_produccion_diaria()
        
        encabezados_prod = ['Fecha', 'Lote', 'Galpón', 'Huevos Buenos', 'Huevos Rotos', 'Huevos Sucios', 'Total', '% Postura', 'Mortalidad']
        for i, encabezado in enumerate(encabezados_prod, start=1):
            celda = ws_produccion.cell(row=1, column=i, value=encabezado)
            celda.font = Font(bold=True)
            celda.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        for i, dato in enumerate(datos_produccion, start=2):
            ws_produccion.cell(row=i, column=1, value=dato['fecha'])
            ws_produccion.cell(row=i, column=2, value=dato['lote'])
            ws_produccion.cell(row=i, column=3, value=dato['galpon'])
            ws_produccion.cell(row=i, column=4, value=dato['huevos_buenos'])
            ws_produccion.cell(row=i, column=5, value=dato['huevos_rotos'])
            ws_produccion.cell(row=i, column=6, value=dato['huevos_sucios'])
            ws_produccion.cell(row=i, column=7, value=dato['total_huevos'])
            ws_produccion.cell(row=i, column=8, value=dato['porcentaje_postura'])
            ws_produccion.cell(row=i, column=9, value=dato['mortalidad'])
        
        # Guardar en buffer
        import io
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="datos_completos_avicola.xlsx"'
        return response
        
    except ImportError:
        raise ImportError("openpyxl no está disponible")

def generar_csv_datos_completos(incluir_historicos=False):
    """
    Genera CSV con todos los datos del módulo avícola
    """
    import csv
    import io
    
    response = HttpResponse(content_type='text/csv')
    fecha_actual = datetime.now().strftime('%Y%m%d')
    response['Content-Disposition'] = f'attachment; filename="datos_completos_avicola_{fecha_actual}.csv"'
    
    writer = csv.writer(response)
    
    # Escribir datos de lotes
    writer.writerow(['=== LOTES ==='])
    writer.writerow(['Código', 'Nombre', 'Galpón', 'Línea Genética', 'Fecha Ingreso', 'Cantidad Inicial', 'Cantidad Actual', 'Estado'])
    
    filtro_lotes = {} if incluir_historicos else {'estado': 'activo'}
    lotes = LoteAves.objects.filter(**filtro_lotes).select_related('galpon', 'linea_genetica')
    
    for lote in lotes:
        writer.writerow([
            lote.codigo,
            lote.nombre_lote,
            lote.galpon.nombre,
            lote.linea_genetica.nombre,
            lote.fecha_ingreso.strftime('%Y-%m-%d'),
            lote.cantidad_inicial,
            lote.cantidad_actual,
            lote.get_estado_display()
        ])
    
    # Escribir datos de producción
    writer.writerow([])  # Línea vacía
    writer.writerow(['=== PRODUCCIÓN ==='])
    writer.writerow(['Fecha', 'Lote', 'Galpón', 'Huevos Buenos', 'Huevos Rotos', 'Huevos Sucios', 'Total', '% Postura', 'Mortalidad'])
    
    from .reports import ReporteAvicola
    parametros = {}
    if not incluir_historicos:
        parametros['fecha_inicio'] = timezone.now().date() - timedelta(days=90)
    
    reporte = ReporteAvicola(parametros)
    datos_produccion = reporte.obtener_datos_produccion_diaria()
    
    for dato in datos_produccion:
        writer.writerow([
            dato['fecha'].strftime('%Y-%m-%d'),
            dato['lote'],
            dato['galpon'],
            dato['huevos_buenos'],
            dato['huevos_rotos'],
            dato['huevos_sucios'],
            dato['total_huevos'],
            dato['porcentaje_postura'],
            dato['mortalidad']
        ])
    
    return response
"""
Sistema de reportes específicos para el módulo avícola
"""

import os
import io
import csv
from datetime import datetime, timedelta, date
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Avg, Count, Q, F, Max, Min
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

# Importaciones para PDF y Excel
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.chart import BarChart, LineChart, Reference, PieChart
    from openpyxl.utils.dataframe import dataframe_to_rows
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from .models import (
    LoteAves, BitacoraDiaria, MovimientoHuevos, ConsumoConcentrado,
    RegistroVacunacion, AlertaSistema, Galpon, LineaGenetica
)

class ReporteAvicola:
    """
    Clase principal para generar reportes avícolas
    """
    
    def __init__(self, parametros=None):
        self.parametros = parametros or {}
        self.fecha_inicio = self.parametros.get('fecha_inicio')
        self.fecha_fin = self.parametros.get('fecha_fin')
        self.lote_id = self.parametros.get('lote_id')
        self.galpon_id = self.parametros.get('galpon_id')
        
    def obtener_datos_produccion_diaria(self):
        """
        Obtiene datos de producción diaria de huevos
        """
        filtros = {}
        if self.fecha_inicio:
            filtros['fecha__gte'] = self.fecha_inicio
        if self.fecha_fin:
            filtros['fecha__lte'] = self.fecha_fin
        if self.lote_id:
            filtros['lote_id'] = self.lote_id
        if self.galpon_id:
            filtros['lote__galpon_id'] = self.galpon_id
            
        bitacoras = BitacoraDiaria.objects.filter(**filtros).select_related(
            'lote', 'lote__galpon', 'lote__linea_genetica'
        ).order_by('fecha')
        
        datos = []
        for bitacora in bitacoras:
            porcentaje_postura = (bitacora.huevos_buenos / bitacora.lote.cantidad_actual * 100) if bitacora.lote.cantidad_actual > 0 else 0
            datos.append({
                'fecha': bitacora.fecha,
                'lote': bitacora.lote.codigo,
                'galpon': bitacora.lote.galpon.nombre,
                'huevos_buenos': bitacora.huevos_buenos,
                'huevos_rotos': bitacora.huevos_rotos,
                'huevos_sucios': bitacora.huevos_sucios,
                'total_huevos': bitacora.huevos_buenos + bitacora.huevos_rotos + bitacora.huevos_sucios,
                'porcentaje_postura': round(porcentaje_postura, 2),
                'mortalidad': bitacora.mortalidad,
                'temperatura_max': bitacora.temperatura_maxima,
                'temperatura_min': bitacora.temperatura_minima,
                'humedad': bitacora.humedad_promedio,
                'observaciones': bitacora.observaciones
            })
            
        return datos
    
    def obtener_resumen_produccion(self):
        """
        Obtiene resumen estadístico de producción
        """
        filtros = {}
        if self.fecha_inicio:
            filtros['fecha__gte'] = self.fecha_inicio
        if self.fecha_fin:
            filtros['fecha__lte'] = self.fecha_fin
        if self.lote_id:
            filtros['lote_id'] = self.lote_id
        if self.galpon_id:
            filtros['lote__galpon_id'] = self.galpon_id
            
        bitacoras = BitacoraDiaria.objects.filter(**filtros)
        
        resumen = bitacoras.aggregate(
            total_huevos_buenos=Sum('huevos_buenos'),
            total_huevos_rotos=Sum('huevos_rotos'),
            total_huevos_sucios=Sum('huevos_sucios'),
            total_mortalidad=Sum('mortalidad'),
            promedio_temperatura_max=Avg('temperatura_maxima'),
            promedio_temperatura_min=Avg('temperatura_minima'),
            promedio_humedad=Avg('humedad_promedio'),
            dias_registrados=Count('id')
        )
        
        # Calcular totales
        total_huevos = (resumen['total_huevos_buenos'] or 0) + (resumen['total_huevos_rotos'] or 0) + (resumen['total_huevos_sucios'] or 0)
        
        # Calcular porcentajes
        porcentaje_buenos = (resumen['total_huevos_buenos'] / total_huevos * 100) if total_huevos > 0 else 0
        porcentaje_rotos = (resumen['total_huevos_rotos'] / total_huevos * 100) if total_huevos > 0 else 0
        porcentaje_sucios = (resumen['total_huevos_sucios'] / total_huevos * 100) if total_huevos > 0 else 0
        
        return {
            'total_huevos': total_huevos,
            'huevos_buenos': resumen['total_huevos_buenos'] or 0,
            'huevos_rotos': resumen['total_huevos_rotos'] or 0,
            'huevos_sucios': resumen['total_huevos_sucios'] or 0,
            'porcentaje_buenos': round(porcentaje_buenos, 2),
            'porcentaje_rotos': round(porcentaje_rotos, 2),
            'porcentaje_sucios': round(porcentaje_sucios, 2),
            'total_mortalidad': resumen['total_mortalidad'] or 0,
            'promedio_temperatura_max': round(resumen['promedio_temperatura_max'] or 0, 1),
            'promedio_temperatura_min': round(resumen['promedio_temperatura_min'] or 0, 1),
            'promedio_humedad': round(resumen['promedio_humedad'] or 0, 1),
            'dias_registrados': resumen['dias_registrados']
        }
    
    def obtener_datos_movimiento_huevos(self):
        """
        Obtiene datos de movimiento de huevos
        """
        filtros = {}
        if self.fecha_inicio:
            filtros['fecha__gte'] = self.fecha_inicio
        if self.fecha_fin:
            filtros['fecha__lte'] = self.fecha_fin
        if self.lote_id:
            filtros['lote_id'] = self.lote_id
            
        movimientos = MovimientoHuevos.objects.filter(**filtros).select_related(
            'lote', 'categoria_huevo'
        ).order_by('-fecha')
        
        datos = []
        for mov in movimientos:
            datos.append({
                'fecha': mov.fecha,
                'lote': mov.lote.codigo,
                'tipo_movimiento': mov.get_tipo_movimiento_display(),
                'categoria': mov.categoria_huevo.nombre,
                'cantidad': mov.cantidad,
                'precio_unitario': mov.precio_unitario,
                'valor_total': mov.cantidad * mov.precio_unitario,
                'destino': mov.destino,
                'observaciones': mov.observaciones
            })
            
        return datos
    
    def obtener_datos_consumo_concentrado(self):
        """
        Obtiene datos de consumo de concentrado
        """
        filtros = {}
        if self.fecha_inicio:
            filtros['fecha__gte'] = self.fecha_inicio
        if self.fecha_fin:
            filtros['fecha__lte'] = self.fecha_fin
        if self.lote_id:
            filtros['lote_id'] = self.lote_id
            
        consumos = ConsumoConcentrado.objects.filter(**filtros).select_related(
            'lote', 'tipo_concentrado'
        ).order_by('fecha')
        
        datos = []
        for consumo in consumos:
            datos.append({
                'fecha': consumo.fecha,
                'lote': consumo.lote.codigo,
                'tipo_concentrado': consumo.tipo_concentrado.nombre,
                'cantidad_kg': consumo.cantidad_kg,
                'costo_unitario': consumo.costo_unitario,
                'costo_total': consumo.cantidad_kg * consumo.costo_unitario,
                'observaciones': consumo.observaciones
            })
            
        return datos
    
    def obtener_datos_vacunacion(self):
        """
        Obtiene datos de vacunación
        """
        filtros = {}
        if self.fecha_inicio:
            filtros['fecha_aplicacion__gte'] = self.fecha_inicio
        if self.fecha_fin:
            filtros['fecha_aplicacion__lte'] = self.fecha_fin
        if self.lote_id:
            filtros['lote_id'] = self.lote_id
            
        vacunaciones = RegistroVacunacion.objects.filter(**filtros).select_related(
            'lote', 'plan_vacunacion', 'plan_vacunacion__tipo_vacuna'
        ).order_by('fecha_aplicacion')
        
        datos = []
        for vac in vacunaciones:
            datos.append({
                'fecha_aplicacion': vac.fecha_aplicacion,
                'lote': vac.lote.codigo,
                'vacuna': vac.plan_vacunacion.tipo_vacuna.nombre,
                'dosis_aplicada': vac.dosis_aplicada,
                'via_administracion': vac.get_via_administracion_display(),
                'veterinario': vac.veterinario_responsable,
                'observaciones': vac.observaciones,
                'reacciones_adversas': vac.reacciones_adversas
            })
            
        return datos
    
    def generar_pdf_produccion(self, nombre_archivo="reporte_produccion.pdf"):
        """
        Genera reporte PDF de producción
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab no está disponible")
            
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        story.append(Paragraph("Reporte de Producción Avícola", titulo_style))
        story.append(Spacer(1, 20))
        
        # Información del reporte
        info_data = [
            ['Fecha de generación:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Período:', f"{self.fecha_inicio or 'N/A'} - {self.fecha_fin or 'N/A'}"],
        ]
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Resumen estadístico
        resumen = self.obtener_resumen_produccion()
        story.append(Paragraph("Resumen Estadístico", styles['Heading2']))
        
        resumen_data = [
            ['Concepto', 'Valor'],
            ['Total de huevos producidos', f"{resumen['total_huevos']:,}"],
            ['Huevos buenos', f"{resumen['huevos_buenos']:,} ({resumen['porcentaje_buenos']}%)"],
            ['Huevos rotos', f"{resumen['huevos_rotos']:,} ({resumen['porcentaje_rotos']}%)"],
            ['Huevos sucios', f"{resumen['huevos_sucios']:,} ({resumen['porcentaje_sucios']}%)"],
            ['Total mortalidad', f"{resumen['total_mortalidad']:,}"],
            ['Temperatura promedio máx.', f"{resumen['promedio_temperatura_max']}°C"],
            ['Temperatura promedio mín.', f"{resumen['promedio_temperatura_min']}°C"],
            ['Humedad promedio', f"{resumen['promedio_humedad']}%"],
            ['Días registrados', f"{resumen['dias_registrados']}"],
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(resumen_table)
        story.append(Spacer(1, 20))
        
        # Datos detallados de producción
        story.append(Paragraph("Detalle de Producción Diaria", styles['Heading2']))
        datos_produccion = self.obtener_datos_produccion_diaria()
        
        if datos_produccion:
            # Encabezados de la tabla
            headers = ['Fecha', 'Lote', 'Galpón', 'H. Buenos', 'H. Rotos', 'H. Sucios', 'Total', '% Postura', 'Mortalidad']
            data = [headers]
            
            for dato in datos_produccion[:50]:  # Limitar a 50 registros para el PDF
                data.append([
                    dato['fecha'].strftime('%d/%m/%Y'),
                    dato['lote'],
                    dato['galpon'],
                    str(dato['huevos_buenos']),
                    str(dato['huevos_rotos']),
                    str(dato['huevos_sucios']),
                    str(dato['total_huevos']),
                    f"{dato['porcentaje_postura']}%",
                    str(dato['mortalidad'])
                ])
            
            produccion_table = Table(data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch])
            produccion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(produccion_table)
        
        doc.build(story)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response
    
    def generar_excel_produccion(self, nombre_archivo="reporte_produccion.xlsx"):
        """
        Genera reporte Excel de producción con múltiples hojas y gráficos
        """
        if not OPENPYXL_AVAILABLE:
            raise ImportError("openpyxl no está disponible")
            
        wb = openpyxl.Workbook()
        
        # Hoja 1: Resumen
        ws_resumen = wb.active
        ws_resumen.title = "Resumen"
        
        # Título
        ws_resumen['A1'] = "Reporte de Producción Avícola"
        ws_resumen['A1'].font = Font(size=16, bold=True)
        ws_resumen.merge_cells('A1:D1')
        
        # Información del reporte
        ws_resumen['A3'] = "Fecha de generación:"
        ws_resumen['B3'] = datetime.now().strftime('%d/%m/%Y %H:%M')
        ws_resumen['A4'] = "Período:"
        ws_resumen['B4'] = f"{self.fecha_inicio or 'N/A'} - {self.fecha_fin or 'N/A'}"
        
        # Resumen estadístico
        resumen = self.obtener_resumen_produccion()
        ws_resumen['A6'] = "Resumen Estadístico"
        ws_resumen['A6'].font = Font(size=14, bold=True)
        
        datos_resumen = [
            ['Concepto', 'Valor'],
            ['Total de huevos producidos', resumen['total_huevos']],
            ['Huevos buenos', f"{resumen['huevos_buenos']} ({resumen['porcentaje_buenos']}%)"],
            ['Huevos rotos', f"{resumen['huevos_rotos']} ({resumen['porcentaje_rotos']}%)"],
            ['Huevos sucios', f"{resumen['huevos_sucios']} ({resumen['porcentaje_sucios']}%)"],
            ['Total mortalidad', resumen['total_mortalidad']],
            ['Temperatura promedio máx.', f"{resumen['promedio_temperatura_max']}°C"],
            ['Temperatura promedio mín.', f"{resumen['promedio_temperatura_min']}°C"],
            ['Humedad promedio', f"{resumen['promedio_humedad']}%"],
            ['Días registrados', resumen['dias_registrados']],
        ]
        
        for i, fila in enumerate(datos_resumen, start=8):
            for j, valor in enumerate(fila, start=1):
                celda = ws_resumen.cell(row=i, column=j, value=valor)
                if i == 8:  # Encabezado
                    celda.font = Font(bold=True)
                    celda.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Hoja 2: Producción Diaria
        ws_produccion = wb.create_sheet("Producción Diaria")
        datos_produccion = self.obtener_datos_produccion_diaria()
        
        # Encabezados
        encabezados = ['Fecha', 'Lote', 'Galpón', 'Huevos Buenos', 'Huevos Rotos', 'Huevos Sucios', 
                      'Total Huevos', '% Postura', 'Mortalidad', 'Temp. Máx', 'Temp. Mín', 'Humedad', 'Observaciones']
        
        for i, encabezado in enumerate(encabezados, start=1):
            celda = ws_produccion.cell(row=1, column=i, value=encabezado)
            celda.font = Font(bold=True)
            celda.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Datos
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
            ws_produccion.cell(row=i, column=10, value=dato['temperatura_max'])
            ws_produccion.cell(row=i, column=11, value=dato['temperatura_min'])
            ws_produccion.cell(row=i, column=12, value=dato['humedad'])
            ws_produccion.cell(row=i, column=13, value=dato['observaciones'])
        
        # Ajustar ancho de columnas
        for column in ws_produccion.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_produccion.column_dimensions[column_letter].width = adjusted_width
        
        # Hoja 3: Movimiento de Huevos
        ws_movimientos = wb.create_sheet("Movimiento Huevos")
        datos_movimientos = self.obtener_datos_movimiento_huevos()
        
        encabezados_mov = ['Fecha', 'Lote', 'Tipo Movimiento', 'Categoría', 'Cantidad', 'Precio Unitario', 'Valor Total', 'Destino', 'Observaciones']
        
        for i, encabezado in enumerate(encabezados_mov, start=1):
            celda = ws_movimientos.cell(row=1, column=i, value=encabezado)
            celda.font = Font(bold=True)
            celda.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        for i, dato in enumerate(datos_movimientos, start=2):
            ws_movimientos.cell(row=i, column=1, value=dato['fecha'])
            ws_movimientos.cell(row=i, column=2, value=dato['lote'])
            ws_movimientos.cell(row=i, column=3, value=dato['tipo_movimiento'])
            ws_movimientos.cell(row=i, column=4, value=dato['categoria'])
            ws_movimientos.cell(row=i, column=5, value=dato['cantidad'])
            ws_movimientos.cell(row=i, column=6, value=dato['precio_unitario'])
            ws_movimientos.cell(row=i, column=7, value=dato['valor_total'])
            ws_movimientos.cell(row=i, column=8, value=dato['destino'])
            ws_movimientos.cell(row=i, column=9, value=dato['observaciones'])
        
        # Crear gráfico de producción
        if datos_produccion:
            chart = LineChart()
            chart.title = "Evolución de la Producción de Huevos"
            chart.style = 13
            chart.x_axis.title = 'Fecha'
            chart.y_axis.title = 'Cantidad de Huevos'
            
            # Datos para el gráfico (últimos 30 días)
            datos_grafico = datos_produccion[-30:] if len(datos_produccion) > 30 else datos_produccion
            
            # Agregar datos del gráfico en una nueva hoja
            ws_grafico = wb.create_sheet("Datos Gráfico")
            ws_grafico['A1'] = "Fecha"
            ws_grafico['B1'] = "Huevos Buenos"
            ws_grafico['C1'] = "Total Huevos"
            
            for i, dato in enumerate(datos_grafico, start=2):
                ws_grafico.cell(row=i, column=1, value=dato['fecha'].strftime('%d/%m'))
                ws_grafico.cell(row=i, column=2, value=dato['huevos_buenos'])
                ws_grafico.cell(row=i, column=3, value=dato['total_huevos'])
            
            # Configurar referencias del gráfico
            data = Reference(ws_grafico, min_col=2, min_row=1, max_col=3, max_row=len(datos_grafico)+1)
            cats = Reference(ws_grafico, min_col=1, min_row=2, max_row=len(datos_grafico)+1)
            
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            
            # Agregar gráfico a la hoja de resumen
            ws_resumen.add_chart(chart, "F6")
        
        # Guardar en buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response
    
    def generar_csv_produccion(self, nombre_archivo="reporte_produccion.csv"):
        """
        Genera reporte CSV de producción
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        
        writer = csv.writer(response)
        
        # Encabezados
        writer.writerow([
            'Fecha', 'Lote', 'Galpón', 'Huevos Buenos', 'Huevos Rotos', 'Huevos Sucios',
            'Total Huevos', '% Postura', 'Mortalidad', 'Temp. Máx', 'Temp. Mín', 'Humedad', 'Observaciones'
        ])
        
        # Datos
        datos_produccion = self.obtener_datos_produccion_diaria()
        for dato in datos_produccion:
            writer.writerow([
                dato['fecha'].strftime('%d/%m/%Y'),
                dato['lote'],
                dato['galpon'],
                dato['huevos_buenos'],
                dato['huevos_rotos'],
                dato['huevos_sucios'],
                dato['total_huevos'],
                dato['porcentaje_postura'],
                dato['mortalidad'],
                dato['temperatura_max'],
                dato['temperatura_min'],
                dato['humedad'],
                dato['observaciones']
            ])
        
        return response

class ReporteComparativo:
    """
    Clase para generar reportes comparativos entre lotes, períodos, etc.
    """
    
    def __init__(self, parametros=None):
        self.parametros = parametros or {}
        
    def comparar_lotes(self, lotes_ids, fecha_inicio, fecha_fin):
        """
        Compara producción entre diferentes lotes
        """
        datos_comparacion = []
        
        for lote_id in lotes_ids:
            lote = get_object_or_404(LoteAves, id=lote_id)
            
            # Obtener datos del lote
            bitacoras = BitacoraDiaria.objects.filter(
                lote_id=lote_id,
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin
            )
            
            resumen = bitacoras.aggregate(
                total_huevos_buenos=Sum('huevos_buenos'),
                total_huevos_rotos=Sum('huevos_rotos'),
                total_huevos_sucios=Sum('huevos_sucios'),
                total_mortalidad=Sum('mortalidad'),
                promedio_postura=Avg(F('huevos_buenos') / F('lote__cantidad_actual') * 100),
                dias_registrados=Count('id')
            )
            
            total_huevos = (resumen['total_huevos_buenos'] or 0) + (resumen['total_huevos_rotos'] or 0) + (resumen['total_huevos_sucios'] or 0)
            
            datos_comparacion.append({
                'lote_codigo': lote.codigo,
                'lote_nombre': lote.nombre_lote,
                'galpon': lote.galpon.nombre,
                'linea_genetica': lote.linea_genetica.nombre,
                'cantidad_aves': lote.cantidad_actual,
                'total_huevos': total_huevos,
                'huevos_buenos': resumen['total_huevos_buenos'] or 0,
                'huevos_rotos': resumen['total_huevos_rotos'] or 0,
                'huevos_sucios': resumen['total_huevos_sucios'] or 0,
                'total_mortalidad': resumen['total_mortalidad'] or 0,
                'promedio_postura': round(resumen['promedio_postura'] or 0, 2),
                'dias_registrados': resumen['dias_registrados'],
                'huevos_por_ave_dia': round(total_huevos / (lote.cantidad_actual * resumen['dias_registrados']), 3) if lote.cantidad_actual > 0 and resumen['dias_registrados'] > 0 else 0
            })
        
        return datos_comparacion
    
    def comparar_periodos(self, lote_id, periodos):
        """
        Compara producción del mismo lote en diferentes períodos
        """
        datos_comparacion = []
        
        for periodo in periodos:
            fecha_inicio = periodo['fecha_inicio']
            fecha_fin = periodo['fecha_fin']
            nombre_periodo = periodo['nombre']
            
            bitacoras = BitacoraDiaria.objects.filter(
                lote_id=lote_id,
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin
            )
            
            resumen = bitacoras.aggregate(
                total_huevos_buenos=Sum('huevos_buenos'),
                total_huevos_rotos=Sum('huevos_rotos'),
                total_huevos_sucios=Sum('huevos_sucios'),
                total_mortalidad=Sum('mortalidad'),
                promedio_temperatura=Avg('temperatura_maxima'),
                promedio_humedad=Avg('humedad_promedio'),
                dias_registrados=Count('id')
            )
            
            total_huevos = (resumen['total_huevos_buenos'] or 0) + (resumen['total_huevos_rotos'] or 0) + (resumen['total_huevos_sucios'] or 0)
            
            datos_comparacion.append({
                'periodo': nombre_periodo,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'total_huevos': total_huevos,
                'huevos_buenos': resumen['total_huevos_buenos'] or 0,
                'huevos_rotos': resumen['total_huevos_rotos'] or 0,
                'huevos_sucios': resumen['total_huevos_sucios'] or 0,
                'total_mortalidad': resumen['total_mortalidad'] or 0,
                'promedio_temperatura': round(resumen['promedio_temperatura'] or 0, 1),
                'promedio_humedad': round(resumen['promedio_humedad'] or 0, 1),
                'dias_registrados': resumen['dias_registrados'],
                'promedio_huevos_dia': round(total_huevos / resumen['dias_registrados'], 1) if resumen['dias_registrados'] > 0 else 0
            })
        
        return datos_comparacion

def obtener_datos_dashboard():
    """
    Obtiene datos para el dashboard principal del módulo avícola
    """
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    
    # Estadísticas generales
    total_lotes_activos = LoteAves.objects.filter(estado='activo').count()
    total_aves = LoteAves.objects.filter(estado='activo').aggregate(total=Sum('cantidad_actual'))['total'] or 0
    
    # Producción del día
    produccion_hoy = BitacoraDiaria.objects.filter(fecha=hoy).aggregate(
        huevos_hoy=Sum('huevos_buenos'),
        mortalidad_hoy=Sum('mortalidad')
    )
    
    # Producción últimos 30 días
    produccion_30_dias = BitacoraDiaria.objects.filter(
        fecha__gte=hace_30_dias,
        fecha__lte=hoy
    ).aggregate(
        total_huevos=Sum('huevos_buenos'),
        promedio_diario=Avg('huevos_buenos')
    )
    
    # Alertas activas
    alertas_activas = AlertaSistema.objects.filter(
        estado='activa',
        fecha_creacion__gte=hace_30_dias
    ).count()
    
    # Evolución de producción (últimos 7 días)
    evolucion_produccion = []
    for i in range(7):
        fecha = hoy - timedelta(days=i)
        produccion_dia = BitacoraDiaria.objects.filter(fecha=fecha).aggregate(
            total=Sum('huevos_buenos')
        )['total'] or 0
        evolucion_produccion.append({
            'fecha': fecha.strftime('%d/%m'),
            'produccion': produccion_dia
        })
    
    evolucion_produccion.reverse()
    
    # Top 5 lotes por producción
    top_lotes = BitacoraDiaria.objects.filter(
        fecha__gte=hace_30_dias
    ).values(
        'lote__codigo', 'lote__nombre_lote'
    ).annotate(
        total_produccion=Sum('huevos_buenos')
    ).order_by('-total_produccion')[:5]
    
    return {
        'total_lotes_activos': total_lotes_activos,
        'total_aves': total_aves,
        'huevos_hoy': produccion_hoy['huevos_hoy'] or 0,
        'mortalidad_hoy': produccion_hoy['mortalidad_hoy'] or 0,
        'total_huevos_30_dias': produccion_30_dias['total_huevos'] or 0,
        'promedio_diario_30_dias': round(produccion_30_dias['promedio_diario'] or 0, 1),
        'alertas_activas': alertas_activas,
        'evolucion_produccion': evolucion_produccion,
        'top_lotes': list(top_lotes)
    }
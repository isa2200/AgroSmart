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
    LoteAves, BitacoraDiaria, MovimientoHuevos, ControlConcentrado,
    PlanVacunacion, AlertaSistema, TipoVacuna, TipoConcentrado
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
        
    def obtener_datos_produccion_diaria(self):
        """
        Obtiene datos de producción diaria con filtros aplicados
        """
        queryset = BitacoraDiaria.objects.all()
        
        if self.lote_id:
            queryset = queryset.filter(lote_id=self.lote_id)
        if self.fecha_inicio:
            queryset = queryset.filter(fecha__gte=self.fecha_inicio)
        if self.fecha_fin:
            queryset = queryset.filter(fecha__lte=self.fecha_fin)
            
        return queryset.select_related('lote').order_by('-fecha')
    
    def obtener_resumen_produccion(self):
        """
        Obtiene resumen estadístico de producción
        """
        datos = self.obtener_datos_produccion_diaria()
        
        if not datos.exists():
            return {
                'total_huevos': 0,
                'produccion_aaa': 0,
                'produccion_aa': 0,
                'produccion_a': 0,
                'produccion_b': 0,
                'produccion_c': 0,
                'total_mortalidad': 0,
                'promedio_diario': 0,
                'mejor_dia': 0,
                'total_consumo': 0,
                'porcentaje_postura': 0,
                'dias_registrados': 0
            }
            
        resumen = datos.aggregate(
            total_huevos=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')),
            produccion_aaa=Sum('produccion_aaa'),
            produccion_aa=Sum('produccion_aa'),
            produccion_a=Sum('produccion_a'),
            produccion_b=Sum('produccion_b'),
            produccion_c=Sum('produccion_c'),
            total_mortalidad=Sum('mortalidad'),
            promedio_diario=Avg(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')),
            mejor_dia=Max(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')),
            total_consumo=Sum('consumo_concentrado'),
            dias_registrados=Count('id')
        )
        
        # Calcular porcentaje de postura promedio
        total_aves = 0
        total_produccion = 0
        
        for registro in datos:
            aves_dia = registro.lote.numero_aves_actual
            produccion_dia = (registro.produccion_aaa + registro.produccion_aa + 
                            registro.produccion_a + registro.produccion_b + registro.produccion_c)
            total_aves += aves_dia
            total_produccion += produccion_dia
            
        porcentaje_postura = (total_produccion / total_aves * 100) if total_aves > 0 else 0
        
        # Calcular porcentajes por categoría
        total_huevos = resumen['total_huevos'] or 0
        porcentaje_aaa = (resumen['produccion_aaa'] / total_huevos * 100) if total_huevos > 0 else 0
        porcentaje_aa = (resumen['produccion_aa'] / total_huevos * 100) if total_huevos > 0 else 0
        porcentaje_a = (resumen['produccion_a'] / total_huevos * 100) if total_huevos > 0 else 0
        porcentaje_b = (resumen['produccion_b'] / total_huevos * 100) if total_huevos > 0 else 0
        porcentaje_c = (resumen['produccion_c'] / total_huevos * 100) if total_huevos > 0 else 0
        
        return {
            'total_huevos': total_huevos,
            'produccion_aaa': resumen['produccion_aaa'] or 0,
            'produccion_aa': resumen['produccion_aa'] or 0,
            'produccion_a': resumen['produccion_a'] or 0,
            'produccion_b': resumen['produccion_b'] or 0,
            'produccion_c': resumen['produccion_c'] or 0,
            'porcentaje_aaa': round(porcentaje_aaa, 2),
            'porcentaje_aa': round(porcentaje_aa, 2),
            'porcentaje_a': round(porcentaje_a, 2),
            'porcentaje_b': round(porcentaje_b, 2),
            'porcentaje_c': round(porcentaje_c, 2),
            'total_mortalidad': resumen['total_mortalidad'] or 0,
            'promedio_diario': round(resumen['promedio_diario'] or 0, 1),
            'mejor_dia': resumen['mejor_dia'] or 0,
            'total_consumo': resumen['total_consumo'] or 0,
            'porcentaje_postura': round(porcentaje_postura, 2),
            'dias_registrados': resumen['dias_registrados']
        }
    
    def obtener_datos_movimiento_huevos(self):
        """
        Obtiene datos de movimientos de huevos
        """
        queryset = MovimientoHuevos.objects.all()
        
        if self.fecha_inicio:
            queryset = queryset.filter(fecha__gte=self.fecha_inicio)
        if self.fecha_fin:
            queryset = queryset.filter(fecha__lte=self.fecha_fin)
            
        return queryset.prefetch_related('detalles').order_by('-fecha')
    
    def obtener_datos_consumo_concentrado(self):
        """
        Obtiene datos de consumo de concentrado
        """
        queryset = ControlConcentrado.objects.filter(tipo_movimiento='salida')
        
        if self.lote_id:
            queryset = queryset.filter(lote_id=self.lote_id)
        if self.fecha_inicio:
            queryset = queryset.filter(fecha__gte=self.fecha_inicio)
        if self.fecha_fin:
            queryset = queryset.filter(fecha__lte=self.fecha_fin)
            
        return queryset.select_related('tipo_concentrado', 'lote').order_by('-fecha')
    
    def obtener_datos_vacunacion(self):
        """
        Obtiene datos de vacunación
        """
        queryset = PlanVacunacion.objects.all()
        
        if self.lote_id:
            queryset = queryset.filter(lote_id=self.lote_id)
        if self.fecha_inicio:
            queryset = queryset.filter(fecha_programada__gte=self.fecha_inicio)
        if self.fecha_fin:
            queryset = queryset.filter(fecha_programada__lte=self.fecha_fin)
            
        return queryset.select_related('lote', 'tipo_vacuna', 'veterinario').order_by('-fecha_programada')
    
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
            ['Producción AAA', f"{resumen['produccion_aaa']:,} ({resumen['porcentaje_aaa']}%)"],
            ['Producción AA', f"{resumen['produccion_aa']:,} ({resumen['porcentaje_aa']}%)"],
            ['Producción A', f"{resumen['produccion_a']:,} ({resumen['porcentaje_a']}%)"],
            ['Producción B', f"{resumen['produccion_b']:,} ({resumen['porcentaje_b']}%)"],
            ['Producción C', f"{resumen['produccion_c']:,} ({resumen['porcentaje_c']}%)"],
            ['Total mortalidad', f"{resumen['total_mortalidad']:,}"],
            ['Días registrados', f"{resumen['dias_registrados']}"],
            ['Promedio diario', f"{resumen['promedio_diario']:,}"],
            ['% Postura promedio', f"{resumen['porcentaje_postura']}%"],
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
            headers = ['Fecha', 'Lote', 'Galpón', 'AAA', 'AA', 'A', 'B', 'C', 'Total', 'Mortalidad']
            data = [headers]
            
            for dato in datos_produccion[:50]:  # Limitar a 50 registros para el PDF
                total_huevos = dato.produccion_aaa + dato.produccion_aa + dato.produccion_a + dato.produccion_b + dato.produccion_c
                data.append([
                    dato.fecha.strftime('%d/%m/%Y'),
                    dato.lote.codigo,
                    dato.lote.galpon,
                    str(dato.produccion_aaa),
                    str(dato.produccion_aa),
                    str(dato.produccion_a),
                    str(dato.produccion_b),
                    str(dato.produccion_c),
                    str(total_huevos),
                    str(dato.mortalidad)
                ])
            
            produccion_table = Table(data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.6*inch, 0.6*inch])
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
            ['Producción AAA', f"{resumen['produccion_aaa']} ({resumen['porcentaje_aaa']}%)"],
            ['Producción AA', f"{resumen['produccion_aa']} ({resumen['porcentaje_aa']}%)"],
            ['Producción A', f"{resumen['produccion_a']} ({resumen['porcentaje_a']}%)"],
            ['Producción B', f"{resumen['produccion_b']} ({resumen['porcentaje_b']}%)"],
            ['Producción C', f"{resumen['produccion_c']} ({resumen['porcentaje_c']}%)"],
            ['Total mortalidad', resumen['total_mortalidad']],
            ['Días registrados', resumen['dias_registrados']],
            ['Promedio diario', resumen['promedio_diario']],
            ['% Postura promedio', f"{resumen['porcentaje_postura']}%"],
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
        encabezados = ['Fecha', 'Lote', 'Galpón', 'Producción AAA', 'Producción AA', 'Producción A', 
                      'Producción B', 'Producción C', 'Total Huevos', 'Mortalidad', 'Consumo Concentrado', 'Observaciones']
        
        for i, encabezado in enumerate(encabezados, start=1):
            celda = ws_produccion.cell(row=1, column=i, value=encabezado)
            celda.font = Font(bold=True)
            celda.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Datos
        for i, dato in enumerate(datos_produccion, start=2):
            total_huevos = dato.produccion_aaa + dato.produccion_aa + dato.produccion_a + dato.produccion_b + dato.produccion_c
            ws_produccion.cell(row=i, column=1, value=dato.fecha)
            ws_produccion.cell(row=i, column=2, value=dato.lote.codigo)
            ws_produccion.cell(row=i, column=3, value=dato.lote.galpon)
            ws_produccion.cell(row=i, column=4, value=dato.produccion_aaa)
            ws_produccion.cell(row=i, column=5, value=dato.produccion_aa)
            ws_produccion.cell(row=i, column=6, value=dato.produccion_a)
            ws_produccion.cell(row=i, column=7, value=dato.produccion_b)
            ws_produccion.cell(row=i, column=8, value=dato.produccion_c)
            ws_produccion.cell(row=i, column=9, value=total_huevos)
            ws_produccion.cell(row=i, column=10, value=dato.mortalidad)
            ws_produccion.cell(row=i, column=11, value=float(dato.consumo_concentrado))
            ws_produccion.cell(row=i, column=12, value=dato.observaciones)
        
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
        
        # Crear gráfico de producción
        if datos_produccion:
            chart = LineChart()
            chart.title = "Evolución de la Producción de Huevos"
            chart.style = 13
            chart.x_axis.title = 'Fecha'
            chart.y_axis.title = 'Cantidad de Huevos'
            
            # Datos para el gráfico (últimos 30 días)
            datos_grafico = list(datos_produccion)[-30:] if len(list(datos_produccion)) > 30 else list(datos_produccion)
            
            # Agregar datos del gráfico en una nueva hoja
            ws_grafico = wb.create_sheet("Datos Gráfico")
            ws_grafico['A1'] = "Fecha"
            ws_grafico['B1'] = "Total Huevos"
            ws_grafico['C1'] = "Mortalidad"
            
            for i, dato in enumerate(datos_grafico, start=2):
                total_huevos = dato.produccion_aaa + dato.produccion_aa + dato.produccion_a + dato.produccion_b + dato.produccion_c
                ws_grafico.cell(row=i, column=1, value=dato.fecha.strftime('%d/%m'))
                ws_grafico.cell(row=i, column=2, value=total_huevos)
                ws_grafico.cell(row=i, column=3, value=dato.mortalidad)
            
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
            'Fecha', 'Lote', 'Galpón', 'Producción AAA', 'Producción AA', 'Producción A',
            'Producción B', 'Producción C', 'Total Huevos', 'Mortalidad', 'Consumo Concentrado', 'Observaciones'
        ])
        
        # Datos
        datos_produccion = self.obtener_datos_produccion_diaria()
        for dato in datos_produccion:
            total_huevos = dato.produccion_aaa + dato.produccion_aa + dato.produccion_a + dato.produccion_b + dato.produccion_c
            writer.writerow([
                dato.fecha.strftime('%d/%m/%Y'),
                dato.lote.codigo,
                dato.lote.galpon,
                dato.produccion_aaa,
                dato.produccion_aa,
                dato.produccion_a,
                dato.produccion_b,
                dato.produccion_c,
                total_huevos,
                dato.mortalidad,
                float(dato.consumo_concentrado),
                dato.observaciones
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
                total_produccion_aaa=Sum('produccion_aaa'),
                total_produccion_aa=Sum('produccion_aa'),
                total_produccion_a=Sum('produccion_a'),
                total_produccion_b=Sum('produccion_b'),
                total_produccion_c=Sum('produccion_c'),
                total_mortalidad=Sum('mortalidad'),
                promedio_postura=Avg(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')),
                dias_registrados=Count('id')
            )
            
            total_huevos = (
                (resumen['total_produccion_aaa'] or 0) + 
                (resumen['total_produccion_aa'] or 0) + 
                (resumen['total_produccion_a'] or 0) + 
                (resumen['total_produccion_b'] or 0) + 
                (resumen['total_produccion_c'] or 0)
            )
            
            datos_comparacion.append({
                'lote_codigo': lote.codigo,
                'galpon': lote.galpon,
                'linea_genetica': lote.linea_genetica,
                'numero_aves_actual': lote.numero_aves_actual,
                'total_huevos': total_huevos,
                'produccion_aaa': resumen['total_produccion_aaa'] or 0,
                'produccion_aa': resumen['total_produccion_aa'] or 0,
                'produccion_a': resumen['total_produccion_a'] or 0,
                'produccion_b': resumen['total_produccion_b'] or 0,
                'produccion_c': resumen['total_produccion_c'] or 0,
                'total_mortalidad': resumen['total_mortalidad'] or 0,
                'promedio_postura': round(resumen['promedio_postura'] or 0, 2),
                'dias_registrados': resumen['dias_registrados'],
                'huevos_por_ave_dia': round(total_huevos / (lote.numero_aves_actual * resumen['dias_registrados']), 3) if lote.numero_aves_actual > 0 and resumen['dias_registrados'] > 0 else 0
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
                total_produccion_aaa=Sum('produccion_aaa'),
                total_produccion_aa=Sum('produccion_aa'),
                total_produccion_a=Sum('produccion_a'),
                total_produccion_b=Sum('produccion_b'),
                total_produccion_c=Sum('produccion_c'),
                total_mortalidad=Sum('mortalidad'),
                dias_registrados=Count('id')
            )
            
            total_huevos = (
                (resumen['total_produccion_aaa'] or 0) + 
                (resumen['total_produccion_aa'] or 0) + 
                (resumen['total_produccion_a'] or 0) + 
                (resumen['total_produccion_b'] or 0) + 
                (resumen['total_produccion_c'] or 0)
            )
            
            datos_comparacion.append({
                'periodo': nombre_periodo,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'total_huevos': total_huevos,
                'produccion_aaa': resumen['total_produccion_aaa'] or 0,
                'produccion_aa': resumen['total_produccion_aa'] or 0,
                'produccion_a': resumen['total_produccion_a'] or 0,
                'produccion_b': resumen['total_produccion_b'] or 0,
                'produccion_c': resumen['total_produccion_c'] or 0,
                'total_mortalidad': resumen['total_mortalidad'] or 0,
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
    total_lotes_activos = LoteAves.objects.filter(estado__in=['levante', 'postura']).count()
    total_aves = LoteAves.objects.filter(estado__in=['levante', 'postura']).aggregate(total=Sum('numero_aves_actual'))['total'] or 0
    
    # Producción del día
    produccion_hoy = BitacoraDiaria.objects.filter(fecha=hoy).aggregate(
        huevos_hoy=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')),
        mortalidad_hoy=Sum('mortalidad')
    )
    
    # Producción últimos 30 días
    produccion_30_dias = BitacoraDiaria.objects.filter(
        fecha__gte=hace_30_dias,
        fecha__lte=hoy
    ).aggregate(
        total_huevos=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c')),
        promedio_diario=Avg(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c'))
    )
    
    # Alertas activas
    alertas_activas = AlertaSistema.objects.filter(
        leida=False
    ).count()
    
    # Evolución de producción (últimos 7 días)
    evolucion_produccion = []
    for i in range(7):
        fecha = hoy - timedelta(days=i)
        produccion_dia = BitacoraDiaria.objects.filter(fecha=fecha).aggregate(
            total=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c'))
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
        'lote__codigo', 'lote__galpon'
    ).annotate(
        total_produccion=Sum(F('produccion_aaa') + F('produccion_aa') + F('produccion_a') + F('produccion_b') + F('produccion_c'))
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
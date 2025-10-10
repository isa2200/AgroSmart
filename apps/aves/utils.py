"""
Utilidades para el módulo avícola.
"""

from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.chart import BarChart, LineChart, Reference

from .models import AlertaSistema, InventarioHuevos, LoteAves


def generar_alertas():
    """Genera alertas automáticas del sistema."""
    alertas_generadas = []
    
    # Alerta por baja producción
    lotes_activos = LoteAves.objects.filter(is_active=True, estado='postura')
    for lote in lotes_activos:
        # Lógica para detectar baja producción
        pass
    
    return alertas_generadas


def actualizar_inventario_huevos(lote, produccion_data):
    """Actualiza el inventario de huevos automáticamente."""
    try:
        inventario, created = InventarioHuevos.objects.get_or_create(
            lote=lote,
            defaults={
                'stock_aaa': 0,
                'stock_aa': 0,
                'stock_a': 0,
                'stock_b': 0,
                'stock_c': 0,
                'stock_automatico': True
            }
        )
        
        # Actualizar stocks
        inventario.stock_aaa += produccion_data.get('produccion_aaa', 0)
        inventario.stock_aa += produccion_data.get('produccion_aa', 0)
        inventario.stock_a += produccion_data.get('produccion_a', 0)
        inventario.stock_b += produccion_data.get('produccion_b', 0)
        inventario.stock_c += produccion_data.get('produccion_c', 0)
        inventario.save()
        
        return True
    except Exception as e:
        return False


def exportar_reporte_pdf(tipo_reporte, datos, estadisticas):
    """Exporta reportes a PDF con formato mejorado."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = styles['Title']
    title = Paragraph(f"Reporte de {tipo_reporte.title()}", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Fecha de generación
    fecha_style = styles['Normal']
    fecha = Paragraph(f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}", fecha_style)
    story.append(fecha)
    story.append(Spacer(1, 20))
    
    if tipo_reporte == 'produccion':
        # Estadísticas resumen
        stats_data = [
            ['Estadística', 'Valor'],
            ['Total Producción', f"{estadisticas.get('total_produccion', 0):,} huevos"],
            ['Total Mortalidad', f"{estadisticas.get('total_mortalidad', 0):,} aves"],
            ['Consumo Promedio', f"{estadisticas.get('consumo_promedio', 0):.2f} kg/día"],
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Datos detallados
        if datos:
            detail_data = [['Fecha', 'Lote', 'Producción AAA', 'Producción AA', 'Producción A', 'Mortalidad']]
            for bitacora in datos[:50]:  # Limitar a 50 registros
                detail_data.append([
                    bitacora.fecha.strftime('%d/%m/%Y'),
                    bitacora.lote.codigo,
                    str(bitacora.produccion_aaa or 0),
                    str(bitacora.produccion_aa or 0),
                    str(bitacora.produccion_a or 0),
                    str(bitacora.mortalidad or 0),
                ])
            
            detail_table = Table(detail_data)
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(detail_table)
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    return response


def exportar_reporte_excel(tipo_reporte, datos, estadisticas, filtros=None):
    """Exporta reportes a Excel con formato mejorado."""
    try:
        from openpyxl.cell.cell import MergedCell
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Reporte {tipo_reporte.title()}"
        
        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        center_alignment = Alignment(horizontal="center", vertical="center")
        
        # Título
        ws['A1'] = f"Reporte de {tipo_reporte.title()}"
        ws['A1'].font = Font(bold=True, size=16)
        ws.merge_cells('A1:F1')
        
        # Fecha de generación
        ws['A2'] = f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        ws.merge_cells('A2:F2')
        
        # Filtros aplicados
        row = 4
        if filtros:
            ws[f'A{row}'] = "Filtros aplicados:"
            ws[f'A{row}'].font = Font(bold=True)
            row += 1
            for key, value in filtros.items():
                if value:
                    ws[f'A{row}'] = f"{key.replace('_', ' ').title()}: {value}"
                    row += 1
            row += 1
        
        if tipo_reporte == 'produccion':
            # Estadísticas resumen
            ws[f'A{row}'] = "Resumen Estadístico"
            ws[f'A{row}'].font = Font(bold=True, size=14)
            row += 2
            
            stats_headers = ['Estadística', 'Valor']
            for col, header in enumerate(stats_headers, 1):
                cell = ws.cell(row=row, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
            
            row += 1
            # Corregido para manejar valores None
            total_prod = estadisticas.get('total_produccion', 0) or 0
            total_mort = estadisticas.get('total_mortalidad', 0) or 0
            consumo_prom = estadisticas.get('consumo_promedio', 0) or 0
            
            stats_data = [
                ['Total Producción', f"{total_prod:,} huevos"],
                ['Total Mortalidad', f"{total_mort:,} aves"],
                ['Consumo Promedio', f"{consumo_prom:.2f} kg/día"],
            ]
            
            for stat_row in stats_data:
                for col, value in enumerate(stat_row, 1):
                    ws.cell(row=row, column=col, value=value)
                row += 1
            
            row += 2
            
            # Datos detallados
            ws[f'A{row}'] = "Datos Detallados"
            ws[f'A{row}'].font = Font(bold=True, size=14)
            row += 2
            
            headers = ['Fecha', 'Lote', 'Galpón', 'Producción AAA', 'Producción AA', 'Producción A', 'Producción B', 'Producción C', 'Total Huevos', 'Mortalidad', 'Consumo']
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
            
            row += 1
            for bitacora in datos:
                try:
                    data_row = [
                        bitacora.fecha.strftime('%d/%m/%Y'),
                        str(bitacora.lote.codigo),
                        str(bitacora.lote.galpon),
                        int(bitacora.produccion_aaa or 0),
                        int(bitacora.produccion_aa or 0),
                        int(bitacora.produccion_a or 0),
                        int(bitacora.produccion_b or 0),
                        int(bitacora.produccion_c or 0),
                        int((bitacora.produccion_aaa or 0) + (bitacora.produccion_aa or 0) + (bitacora.produccion_a or 0) + (bitacora.produccion_b or 0) + (bitacora.produccion_c or 0)),
                        int(bitacora.mortalidad or 0),
                        float(bitacora.consumo_concentrado or 0),
                    ]
                    for col, value in enumerate(data_row, 1):
                        ws.cell(row=row, column=col, value=value)
                    row += 1
                except Exception as e:
                    # Si hay error con una fila, continuar con la siguiente
                    print(f"Error procesando bitácora {bitacora.id}: {e}")
                    continue
        
        # Ajustar ancho de columnas - corregido para manejar MergedCell
        for col_num in range(1, ws.max_column + 1):
            max_length = 0
            column_letter = openpyxl.utils.get_column_letter(col_num)
            
            for row_num in range(1, ws.max_row + 1):
                cell = ws.cell(row=row_num, column=col_num)
                # Saltar celdas combinadas
                if isinstance(cell, MergedCell):
                    continue
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Guardar en buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timezone.now().strftime("%Y%m%d_%H%M")}.xlsx"'
        
        return response
        
    except ImportError as e:
        from django.http import HttpResponseServerError
        return HttpResponseServerError(f"openpyxl no está instalado. Error: {str(e)}")
    except Exception as e:
        from django.http import HttpResponseServerError
        import traceback
        error_detail = traceback.format_exc()
        return HttpResponseServerError(f"Error al generar archivo Excel: {str(e)}\n{error_detail}")
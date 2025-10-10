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


def generar_alertas(bitacora_instance=None):
    """Genera alertas automáticas del sistema."""
    alertas_generadas = []
    
    if bitacora_instance:
        # Alerta por baja producción basada en la bitácora
        lote = bitacora_instance.lote
        total_produccion = (
            bitacora_instance.produccion_aaa + 
            bitacora_instance.produccion_aa + 
            bitacora_instance.produccion_a + 
            bitacora_instance.produccion_b + 
            bitacora_instance.produccion_c
        )
        
        # Ejemplo: alerta si la producción es muy baja
        if total_produccion < 100:  # Ajustar según criterios
            try:
                alerta, created = AlertaSistema.objects.get_or_create(
                    tipo='baja_produccion',
                    lote=lote,
                    fecha=bitacora_instance.fecha,
                    defaults={
                        'mensaje': f'Baja producción detectada en lote {lote.nombre}: {total_produccion} huevos',
                        'nivel': 'warning',
                        'activa': True
                    }
                )
                if created:
                    alertas_generadas.append(alerta)
            except Exception:
                pass
        
        # Alerta por alta mortalidad
        if bitacora_instance.mortalidad > 5:  # Ajustar según criterios
            try:
                alerta, created = AlertaSistema.objects.get_or_create(
                    tipo='alta_mortalidad',
                    lote=lote,
                    fecha=bitacora_instance.fecha,
                    defaults={
                        'mensaje': f'Alta mortalidad detectada en lote {lote.nombre}: {bitacora_instance.mortalidad} aves',
                        'nivel': 'danger',
                        'activa': True
                    }
                )
                if created:
                    alertas_generadas.append(alerta)
            except Exception:
                pass
    
    return alertas_generadas


def actualizar_inventario_huevos(bitacora_instance):
    """Actualiza el inventario de huevos automáticamente."""
    try:
        lote = bitacora_instance.lote
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
        
        # Actualizar stocks con la producción de la bitácora
        inventario.stock_aaa += bitacora_instance.produccion_aaa
        inventario.stock_aa += bitacora_instance.produccion_aa
        inventario.stock_a += bitacora_instance.produccion_a
        inventario.stock_b += bitacora_instance.produccion_b
        inventario.stock_c += bitacora_instance.produccion_c
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
        
        story.append(Paragraph("Resumen Estadístico", styles['Heading2']))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Datos detallados
        if datos:
            story.append(Paragraph("Datos Detallados", styles['Heading2']))
            
            # Preparar datos para la tabla
            table_data = [['Fecha', 'Lote', 'AAA', 'AA', 'A', 'B', 'C', 'Total', 'Mortalidad']]
            
            for bitacora in datos:
                total_prod = (bitacora.produccion_aaa + bitacora.produccion_aa + 
                            bitacora.produccion_a + bitacora.produccion_b + bitacora.produccion_c)
                
                table_data.append([
                    bitacora.fecha.strftime('%d/%m/%Y'),
                    str(bitacora.lote.nombre),
                    str(bitacora.produccion_aaa),
                    str(bitacora.produccion_aa),
                    str(bitacora.produccion_a),
                    str(bitacora.produccion_b),
                    str(bitacora.produccion_c),
                    str(total_prod),
                    str(bitacora.mortalidad)
                ])
            
            # Crear tabla
            data_table = Table(table_data)
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(data_table)
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    
    # Crear respuesta HTTP
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timezone.now().strftime("%Y%m%d_%H%M")}.pdf"'
    
    return response


def exportar_reporte_excel(tipo_reporte, datos, estadisticas, filtros=None):
    """Exporta reportes a Excel con formato mejorado."""
    try:
        # Crear workbook y worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Reporte {tipo_reporte.title()}"
        
        # Estilos
        title_font = Font(name='Arial', size=16, bold=True, color='FFFFFF')
        header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
        data_font = Font(name='Arial', size=10)
        
        title_fill = PatternFill(start_color='2E7D32', end_color='2E7D32', fill_type='solid')
        header_fill = PatternFill(start_color='4CAF50', end_color='4CAF50', fill_type='solid')
        
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # Título principal
        ws.merge_cells('A1:I1')
        ws['A1'] = f'REPORTE DE {tipo_reporte.upper()}'
        ws['A1'].font = title_font
        ws['A1'].fill = title_fill
        ws['A1'].alignment = center_alignment
        
        # Fecha de generación
        ws.merge_cells('A2:I2')
        ws['A2'] = f'Generado el: {timezone.now().strftime("%d/%m/%Y %H:%M")}'
        ws['A2'].font = Font(name='Arial', size=10, italic=True)
        ws['A2'].alignment = center_alignment
        
        # Resumen Estadístico
        ws.merge_cells('A4:B4')
        ws['A4'] = 'RESUMEN ESTADÍSTICO'
        ws['A4'].font = header_font
        ws['A4'].fill = header_fill
        ws['A4'].alignment = center_alignment
        
        # Estadísticas
        stats_row = 5
        ws[f'A{stats_row}'] = 'Total Producción:'
        ws[f'B{stats_row}'] = f"{estadisticas.get('total_produccion', 0):,} huevos"
        
        stats_row += 1
        ws[f'A{stats_row}'] = 'Total Mortalidad:'
        ws[f'B{stats_row}'] = f"{estadisticas.get('total_mortalidad', 0):,} aves"
        
        stats_row += 1
        ws[f'A{stats_row}'] = 'Consumo Promedio:'
        ws[f'B{stats_row}'] = f"{estadisticas.get('consumo_promedio', 0):.2f} kg/día"
        
        # Datos Detallados
        data_start_row = stats_row + 3
        ws.merge_cells(f'A{data_start_row}:I{data_start_row}')
        ws[f'A{data_start_row}'] = 'DATOS DETALLADOS'
        ws[f'A{data_start_row}'].font = header_font
        ws[f'A{data_start_row}'].fill = header_fill
        ws[f'A{data_start_row}'].alignment = center_alignment
        
        # Encabezados de datos
        headers_row = data_start_row + 1
        headers = ['Fecha', 'Lote', 'AAA', 'AA', 'A', 'B', 'C', 'Total', 'Mortalidad']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=headers_row, column=col)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment
        
        # Datos
        if datos:
            for row_idx, bitacora in enumerate(datos, headers_row + 1):
                total_prod = (bitacora.produccion_aaa + bitacora.produccion_aa + 
                            bitacora.produccion_a + bitacora.produccion_b + bitacora.produccion_c)
                
                row_data = [
                    bitacora.fecha.strftime('%d/%m/%Y'),
                    bitacora.lote.nombre,
                    bitacora.produccion_aaa,
                    bitacora.produccion_aa,
                    bitacora.produccion_a,
                    bitacora.produccion_b,
                    bitacora.produccion_c,
                    total_prod,
                    bitacora.mortalidad
                ]
                
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.value = value
                    cell.font = data_font
                    cell.alignment = center_alignment
        
        # Ajustar ancho de columnas
        from openpyxl.utils import get_column_letter
        from openpyxl.cell import MergedCell
        
        for col_num in range(1, ws.max_column + 1):
            max_length = 0
            column_letter = get_column_letter(col_num)
            
            for row in ws[column_letter]:
                # Saltar celdas combinadas
                if isinstance(row, MergedCell):
                    continue
                    
                try:
                    if len(str(row.value)) > max_length:
                        max_length = len(str(row.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Guardar en buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        # Crear respuesta HTTP
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timezone.now().strftime("%Y%m%d_%H%M")}.xlsx"'
        
        return response
        
    except Exception as e:
        from django.http import HttpResponseServerError
        import traceback
        error_detail = traceback.format_exc()
        return HttpResponseServerError(f"Error al generar archivo Excel: {str(e)}\n{error_detail}")
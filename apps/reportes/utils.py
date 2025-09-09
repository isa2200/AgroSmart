import os
import io
import csv
from datetime import datetime, timedelta
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone

# Importaciones para PDF y Excel
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.chart import BarChart, LineChart, Reference
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from apps.aves.models import LoteAves, ProduccionHuevos

class GeneradorReportes:
    """
    Clase principal para generar reportes en diferentes formatos
    """
    
    def __init__(self, tipo_reporte, parametros=None):
        self.tipo_reporte = tipo_reporte
        self.parametros = parametros or {}
        self.fecha_inicio = self.parametros.get('fecha_inicio')
        self.fecha_fin = self.parametros.get('fecha_fin')
        
    def obtener_datos_produccion(self):
        """
        Obtiene datos de producción según los parámetros
        """
        datos = {
            'lotes': [],
            'resumen': {}
        }
        
        # Filtros de fecha
        filtros_fecha = {}
        if self.fecha_inicio:
            filtros_fecha['fecha__gte'] = self.fecha_inicio
        if self.fecha_fin:
            filtros_fecha['fecha__lte'] = self.fecha_fin
        
        # Datos de producción por lote
        produccion_lotes = ProduccionHuevos.objects.filter(**filtros_fecha).select_related('lote')
        datos['lotes'] = list(produccion_lotes.values(
            'lote__codigo',
            'lote__nombre_lote',
            'lote__linea',
            'total_huevos',
            'peso_promedio_huevo',
            'fecha'
        ))
        
        # Resumen estadístico
        datos['resumen'] = {
            'total_huevos': produccion_lotes.aggregate(total=Sum('total_huevos'))['total'] or 0,
            'promedio_huevos_lote': produccion_lotes.aggregate(promedio=Avg('total_huevos'))['promedio'] or 0,
        }
        
        return datos
    
    def obtener_datos_inventario(self):
        """
        Obtiene datos de inventario de lotes
        """
        datos = {
            'lotes': {
                'total': LoteAves.objects.filter(estado='activo').count(),
                'por_linea': list(LoteAves.objects.filter(estado='activo')
                                .values('linea')
                                .annotate(cantidad=Count('id'))
                                .order_by('linea')),
                'total_aves': LoteAves.objects.filter(estado='activo')
                            .aggregate(total=Sum('cantidad_actual'))['total'] or 0
            },
        }
        
        return datos
    
    def obtener_datos_produccion(self):
        """
        Obtiene datos de producción según los parámetros
        """
        datos = {
            'aves': [],
            'resumen': {}
        }
        
        # Filtros de fecha
        filtros_fecha = {}
        if self.fecha_inicio:
            filtros_fecha['fecha__gte'] = self.fecha_inicio
        if self.fecha_fin:
            filtros_fecha['fecha__lte'] = self.fecha_fin
        
        # Datos de aves
        produccion_aves = ProduccionHuevos.objects.filter(**filtros_fecha).select_related('ave')
        datos['aves'] = list(produccion_aves.values(
            'ave__identificacion',
            'ave__linea',
            'huevos_recolectados',
            'peso_promedio_huevo',
            'fecha',
            'calidad'
        ))
        
        
        # Resumen estadístico
        datos['resumen'] = {
            'total_huevos': produccion_aves.aggregate(total=Sum('huevos_recolectados'))['total'] or 0,
            'promedio_huevos_ave': produccion_aves.aggregate(promedio=Avg('huevos_recolectados'))['promedio'] or 0,
        }
        
        return datos
    
    def obtener_datos_inventario(self):
        """
        Obtiene datos de inventario de animales
        """
        datos = {
            'aves': {
                'total': LoteAves.objects.filter(estado='activo').count(),
                'por_linea': list(LoteAves.objects.filter(estado='activo')
                                .values('linea')
                                .annotate(cantidad=Count('id'))
                                .order_by('linea')),
                'por_sexo': list(LoteAves.objects.filter(estado='activo')
                                .values('sexo')
                                .annotate(cantidad=Count('id'))
                                .order_by('sexo'))
            },
        }
        
        return datos
    
    def generar_pdf(self, datos, nombre_archivo):
        """
        Genera reporte en formato PDF
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab no está instalado. Ejecute: pip install reportlab")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Título del reporte
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        story.append(Paragraph(f"Reporte: {self.tipo_reporte}", title_style))
        story.append(Spacer(1, 12))
        
        # Información del reporte
        info_data = [
            ['Fecha de generación:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Período:', f"{self.fecha_inicio or 'N/A'} - {self.fecha_fin or 'N/A'}"],
        ]
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Contenido según el tipo de reporte
        if 'produccion' in self.tipo_reporte.lower():
            self._agregar_tabla_produccion_pdf(story, datos, styles)
        elif 'inventario' in self.tipo_reporte.lower():
            self._agregar_tabla_inventario_pdf(story, datos, styles)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _agregar_tabla_produccion_pdf(self, story, datos, styles):
        """
        Agrega tabla de producción al PDF
        """
        # Resumen
        story.append(Paragraph("Resumen de Producción", styles['Heading2']))
        resumen_data = [
            ['Tipo', 'Total Producido', 'Unidad'],
            ['Huevos', f"{datos['resumen']['total_huevos']}", 'unidades'],
        ]
        
        resumen_table = Table(resumen_data, colWidths=[2*inch, 2*inch, 1*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(resumen_table)
        story.append(Spacer(1, 20))
    
    def generar_excel(self, datos, nombre_archivo):
        """
        Genera reporte en formato Excel
        """
        if not OPENPYXL_AVAILABLE:
            raise ImportError("openpyxl no está instalado. Ejecute: pip install openpyxl")
        
        wb = openpyxl.Workbook()
        
        # Hoja de resumen
        ws_resumen = wb.active
        ws_resumen.title = "Resumen"
        
        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Título
        ws_resumen['A1'] = f"Reporte: {self.tipo_reporte}"
        ws_resumen['A1'].font = Font(bold=True, size=16)
        ws_resumen['A2'] = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        if 'produccion' in self.tipo_reporte.lower():
            self._crear_hoja_produccion_excel(wb, datos)
        elif 'inventario' in self.tipo_reporte.lower():
            self._crear_hoja_inventario_excel(wb, datos)
        
        # Guardar en buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return buffer
    
    def _crear_hoja_produccion_excel(self, wb, datos):
        """
        Crea hoja de producción en Excel
        """
        if datos['lotes']:
            ws_lotes = wb.create_sheet("Producción Lotes")
            headers = ['Código', 'Nombre Lote', 'Línea', 'Huevos Totales', 'Peso Prom. (g)', 'Fecha']
            ws_lotes.append(headers)
            
            for item in datos['lotes']:
                ws_lotes.append([
                    item['lote__codigo'],
                    item['lote__nombre_lote'],
                    item['lote__linea'],
                    item['total_huevos'],
                    item['peso_promedio_huevo'],
                    item['fecha'].strftime('%d/%m/%Y') if item['fecha'] else ''
                ])
        if datos['aves']:
            ws_aves = wb.create_sheet("Producción Aves")
            headers = ['Identificación', 'Línea', 'Huevos', 'Peso Prom. (g)', 'Fecha', 'Calidad']
            ws_aves.append(headers)
            
            for item in datos['aves']:
                ws_aves.append([
                    item['ave__identificacion'],
                    item['ave__linea'],
                    item['huevos_recolectados'],
                    item['peso_promedio_huevo'],
                    item['fecha'].strftime('%d/%m/%Y') if item['fecha'] else '',
                    item['calidad']
                ])
    
    def generar_csv(self, datos, nombre_archivo):
        """
        Genera reporte en formato CSV
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Escribir encabezado
        writer.writerow([f"Reporte: {self.tipo_reporte}"])
        writer.writerow([f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
        writer.writerow([])  # Línea vacía
        
        if 'produccion' in self.tipo_reporte.lower():
            # Resumen
            writer.writerow(['RESUMEN DE PRODUCCIÓN'])
            writer.writerow(['Tipo', 'Total Producido', 'Unidad'])
            writer.writerow(['Huevos', f"{datos['resumen']['total_huevos']}", 'unidades'])
            writer.writerow([])
        
        buffer.seek(0)
        return buffer

class ReportePersonalizado:
    """
    Clase para crear reportes personalizados con filtros avanzados
    """
    
    def __init__(self, usuario):
        self.usuario = usuario
        self.filtros = {}
        self.campos_seleccionados = []
        self.agrupaciones = []
        self.ordenamiento = []
    
    def agregar_filtro(self, campo, operador, valor):
        """
        Agrega un filtro al reporte
        """
        if campo not in self.filtros:
            self.filtros[campo] = []
        
        self.filtros[campo].append({
            'operador': operador,
            'valor': valor
        })
    
    def seleccionar_campos(self, campos):
        """
        Selecciona los campos a incluir en el reporte
        """
        self.campos_seleccionados = campos
    
    def agrupar_por(self, campos):
        """
        Agrupa los resultados por los campos especificados
        """
        self.agrupaciones = campos
    
    def ordenar_por(self, campos):
        """
        Ordena los resultados por los campos especificados
        """
        self.ordenamiento = campos
    
    def generar_consulta(self, modelo):
        """
        Genera la consulta Django basada en los filtros
        """
        queryset = modelo.objects.all()
        
        # Aplicar filtros
        for campo, filtros_campo in self.filtros.items():
            for filtro in filtros_campo:
                operador = filtro['operador']
                valor = filtro['valor']
                
                if operador == 'igual':
                    queryset = queryset.filter(**{campo: valor})
                elif operador == 'contiene':
                    queryset = queryset.filter(**{f"{campo}__icontains": valor})
                elif operador == 'mayor_que':
                    queryset = queryset.filter(**{f"{campo}__gt": valor})
                elif operador == 'menor_que':
                    queryset = queryset.filter(**{f"{campo}__lt": valor})
                elif operador == 'entre':
                    if isinstance(valor, list) and len(valor) == 2:
                        queryset = queryset.filter(**{f"{campo}__range": valor})
        
        # Aplicar ordenamiento
        if self.ordenamiento:
            queryset = queryset.order_by(*self.ordenamiento)
        
        return queryset

def generar_reporte_automatico(reporte_programado):
    """
    Función para generar reportes automáticos programados
    """
    try:
        generador = GeneradorReportes(
            reporte_programado.tipo_reporte.nombre,
            reporte_programado.parametros
        )
        
        # Obtener datos según el tipo de reporte
        if 'produccion' in reporte_programado.tipo_reporte.nombre.lower():
            datos = generador.obtener_datos_produccion()
        elif 'inventario' in reporte_programado.tipo_reporte.nombre.lower():
            datos = generador.obtener_datos_inventario()
        else:
            datos = {}
        
        # Generar archivo según el formato
        nombre_archivo = f"{reporte_programado.nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if reporte_programado.formato_salida == 'pdf':
            buffer = generador.generar_pdf(datos, nombre_archivo)
            extension = '.pdf'
        elif reporte_programado.formato_salida == 'excel':
            buffer = generador.generar_excel(datos, nombre_archivo)
            extension = '.xlsx'
        elif reporte_programado.formato_salida == 'csv':
            buffer = generador.generar_csv(datos, nombre_archivo)
            extension = '.csv'
        
        # Crear registro del reporte generado
        from .models import ReporteGenerado
        reporte_generado = ReporteGenerado.objects.create(
            tipo_reporte=reporte_programado.tipo_reporte,
            usuario=reporte_programado.usuario,
            nombre_archivo=nombre_archivo + extension,
            formato=reporte_programado.formato_salida,
            parametros=reporte_programado.parametros,
            estado='completado'
        )
        
        # Guardar archivo
        reporte_generado.archivo.save(
            nombre_archivo + extension,
            buffer,
            save=True
        )
        
        # Actualizar fechas del reporte programado
        reporte_programado.ultima_ejecucion = timezone.now()
        # Calcular próxima ejecución según frecuencia
        if reporte_programado.frecuencia == 'diario':
            reporte_programado.proxima_ejecucion = timezone.now() + timedelta(days=1)
        elif reporte_programado.frecuencia == 'semanal':
            reporte_programado.proxima_ejecucion = timezone.now() + timedelta(weeks=1)
        elif reporte_programado.frecuencia == 'mensual':
            reporte_programado.proxima_ejecucion = timezone.now() + timedelta(days=30)
        elif reporte_programado.frecuencia == 'trimestral':
            reporte_programado.proxima_ejecucion = timezone.now() + timedelta(days=90)
        
        reporte_programado.save()
        
        # Enviar por email si está configurado
        if reporte_programado.enviar_email and reporte_programado.emails_destino:
            enviar_reporte_por_email(reporte_generado, reporte_programado.emails_destino)
        
        return reporte_generado
        
    except Exception as e:
        # Registrar error
        from .models import ReporteGenerado
        ReporteGenerado.objects.create(
            tipo_reporte=reporte_programado.tipo_reporte,
            usuario=reporte_programado.usuario,
            nombre_archivo=f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            formato=reporte_programado.formato_salida,
            parametros=reporte_programado.parametros,
            estado='error',
            mensaje_error=str(e)
        )
        raise e

def enviar_reporte_por_email(reporte_generado, emails_destino):
    """
    Envía el reporte generado por email
    """
    from django.core.mail import EmailMessage
    from django.conf import settings
    
    try:
        subject = f"Reporte Automático: {reporte_generado.tipo_reporte.nombre}"
        message = f"""
        Se ha generado automáticamente el reporte: {reporte_generado.tipo_reporte.nombre}
        
        Fecha de generación: {reporte_generado.fecha_generacion.strftime('%d/%m/%Y %H:%M')}
        Formato: {reporte_generado.get_formato_display()}
        
        El archivo se encuentra adjunto a este correo.
        
        Saludos,
        Sistema AgroSmart
        """
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=emails_destino
        )
        
        # Adjuntar archivo
        if reporte_generado.archivo:
            email.attach_file(reporte_generado.archivo.path)
        
        email.send()
        
    except Exception as e:
        print(f"Error enviando email: {e}")
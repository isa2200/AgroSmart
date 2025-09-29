"""
Utilidades para el módulo avícola.
"""

from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

from .models import AlertaSistema, InventarioHuevos, LoteAves


def generar_alertas(bitacora):
    """Genera alertas automáticas basadas en la bitácora."""
    
    # Alerta por mortalidad alta (más del 2% diario)
    porcentaje_mortalidad_diario = (bitacora.mortalidad / bitacora.lote.numero_aves_actual) * 100
    if porcentaje_mortalidad_diario > 2:
        AlertaSistema.objects.create(
            tipo_alerta='mortalidad_alta',
            nivel='warning',
            titulo=f'Mortalidad alta en lote {bitacora.lote.codigo}',
            mensaje=f'Se registró una mortalidad del {porcentaje_mortalidad_diario:.1f}% en el día {bitacora.fecha}',
            lote=bitacora.lote,
            galpon_nombre=bitacora.lote.galpon
        )
    
    # Alerta por producción baja (menos del 70% en aves en postura)
    if bitacora.lote.estado == 'postura':
        porcentaje_postura = bitacora.porcentaje_postura
        if porcentaje_postura < 70:
            AlertaSistema.objects.create(
                tipo_alerta='produccion_baja',
                nivel='warning',
                titulo=f'Producción baja en lote {bitacora.lote.codigo}',
                mensaje=f'Porcentaje de postura del {porcentaje_postura:.1f}% el {bitacora.fecha}',
                lote=bitacora.lote,
                galpon_nombre=bitacora.lote.galpon
            )

    # Nota: Se eliminaron las alertas de temperatura ya que no se desean agregar esos campos


def actualizar_inventario_huevos(bitacora):
    """Actualiza el inventario de huevos basado en la producción."""
    categorias = {
        'AAA': bitacora.produccion_aaa,
        'AA': bitacora.produccion_aa,
        'A': bitacora.produccion_a,
        'B': bitacora.produccion_b,
        'C': bitacora.produccion_c,
    }
    
    for categoria, cantidad in categorias.items():
        if cantidad > 0:
            inventario, created = InventarioHuevos.objects.get_or_create(
                categoria=categoria,
                defaults={'cantidad_actual': 0}
            )
            inventario.cantidad_actual += cantidad
            inventario.save()
            
            # Verificar si necesita reposición
            if inventario.necesita_reposicion:
                AlertaSistema.objects.create(
                    tipo_alerta='stock_bajo',
                    nivel='warning',
                    titulo=f'Stock bajo de huevos categoría {categoria}',
                    mensaje=f'Quedan {inventario.cantidad_actual} huevos de categoría {categoria}. Mínimo: {inventario.cantidad_minima}',
                )


def exportar_reporte_pdf(tipo_reporte, datos, estadisticas):
    """Exporta reportes a PDF."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Reporte de {tipo_reporte.title()}")
    p.drawString(100, 730, f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Contenido básico (aquí puedes expandir según el tipo de reporte)
    y_position = 700
    p.setFont("Helvetica", 12)
    
    if tipo_reporte == 'produccion':
        p.drawString(100, y_position, f"Total de registros: {len(datos)}")
        y_position -= 20
        p.drawString(100, y_position, f"Producción total: {estadisticas.get('total_produccion', 0)} huevos")
        y_position -= 20
        p.drawString(100, y_position, f"Mortalidad total: {estadisticas.get('total_mortalidad', 0)} aves")
        y_position -= 20
        p.drawString(100, y_position, f"Consumo promedio: {estadisticas.get('consumo_promedio', 0):.2f} kg")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo_reporte}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    return response


def verificar_vacunas_pendientes():
    """Verifica vacunas pendientes y genera alertas."""
    from .models import PlanVacunacion
    
    fecha_limite = timezone.now().date() + timezone.timedelta(days=3)
    vacunas_pendientes = PlanVacunacion.objects.filter(
        aplicada=False,
        fecha_programada__lte=fecha_limite
    )
    
    for vacuna in vacunas_pendientes:
        AlertaSistema.objects.get_or_create(
            tipo_alerta='vacuna_pendiente',
            lote=vacuna.lote,
            defaults={
                'nivel': 'warning',
                'titulo': f'Vacuna pendiente para lote {vacuna.lote.codigo}',
                'mensaje': f'La vacuna {vacuna.tipo_vacuna.nombre} debe aplicarse el {vacuna.fecha_programada}',
                'usuario_destinatario': vacuna.veterinario
            }
        )
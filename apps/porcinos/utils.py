"""
Utilidades para el módulo de porcinos.
"""

from .models import AlertaPorcinos

def generar_alertas_porcinos(bitacora_instance=None):
    """Genera alertas automáticas del sistema para porcinos."""
    alertas_generadas = []
    
    if bitacora_instance:
        lote = bitacora_instance.lote
        
        # Alerta por mortalidad alta (ejemplo: > 2 cerdos o > 1% del total)
        # Ajustar umbral según necesidad
        umbral_mortalidad = 2 
        if bitacora_instance.mortalidad >= umbral_mortalidad:
            # Verificar si ya existe alerta para este lote y fecha
            exists = AlertaPorcinos.objects.filter(
                tipo_alerta='mortalidad_alta',
                lote=lote,
                fecha_generacion__date=bitacora_instance.fecha
            ).exists()
            
            if not exists:
                try:
                    AlertaPorcinos.objects.create(
                        tipo_alerta='mortalidad_alta',
                        lote=lote,
                        nivel='critica',
                        titulo='Mortalidad Alta Detectada',
                        mensaje=f'Mortalidad de {bitacora_instance.mortalidad} cerdos en el lote {lote.codigo} (Corral: {lote.corral})',
                        corral_nombre=lote.corral,
                        leida=False
                    )
                    # No agregamos a alertas_generadas porque create no retorna (obj, created)
                    # Pero podemos hacerlo si es necesario
                except Exception:
                    pass

        # Alerta por consumo anormal (ejemplo: 0 consumo si hay cerdos)
        if bitacora_instance.consumo_alimento_kg == 0 and lote.numero_cerdos_actual > 0:
            exists = AlertaPorcinos.objects.filter(
                tipo_alerta='consumo_anormal',
                lote=lote,
                fecha_generacion__date=bitacora_instance.fecha
            ).exists()
            
            if not exists:
                try:
                    AlertaPorcinos.objects.create(
                        tipo_alerta='consumo_anormal',
                        lote=lote,
                        nivel='critica',
                        titulo='Consumo de Alimento Cero',
                        mensaje=f'El lote {lote.codigo} registra 0 kg de consumo de alimento.',
                        corral_nombre=lote.corral,
                        leida=False
                    )
                except Exception:
                    pass
        
        # Alerta por peso bajo (si el peso promedio baja respecto al día anterior)
        # Esto requeriría buscar el registro anterior, lo cual es más costoso.
        # Por simplicidad, alertamos si el peso es 0 (error de registro o problema)
        if bitacora_instance.peso_promedio == 0 and lote.numero_cerdos_actual > 0:
             exists = AlertaPorcinos.objects.filter(
                tipo_alerta='peso_bajo',
                lote=lote,
                fecha_generacion__date=bitacora_instance.fecha
            ).exists()
            
             if not exists:
                 try:
                    AlertaPorcinos.objects.create(
                        tipo_alerta='peso_bajo',
                        lote=lote,
                        nivel='normal',
                        titulo='Peso Promedio Cero',
                        mensaje=f'El lote {lote.codigo} registra 0 kg de peso promedio.',
                        corral_nombre=lote.corral,
                        leida=False
                    )
                 except Exception:
                    pass

    return alertas_generadas

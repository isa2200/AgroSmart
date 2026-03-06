"""
Señales para el módulo de porcinos.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BitacoraDiariaPorcinos
from .utils import generar_alertas_porcinos

@receiver(post_save, sender=BitacoraDiariaPorcinos)
def procesar_bitacora_diaria_porcinos(sender, instance, created, **kwargs):
    """Procesa la bitácora diaria después de guardarla."""
    # Generar alertas automáticas (tanto en creación como en actualización)
    generar_alertas_porcinos(instance)

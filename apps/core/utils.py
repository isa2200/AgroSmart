"""
Utilidades comunes para el proyecto AgroSmart.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import re


def validar_peso(peso):
    """
    Valida que el peso sea un valor positivo y razonable.
    """
    if peso <= 0:
        raise ValidationError('El peso debe ser mayor a 0')
    if peso > 1000:  # Peso máximo razonable en kg
        raise ValidationError('El peso parece demasiado alto')
    return peso


def validar_fecha_no_futura(fecha):
    """
    Valida que la fecha no sea futura.
    """
    if fecha > timezone.now().date():
        raise ValidationError('La fecha no puede ser futura')
    return fecha


def calcular_edad_dias(fecha_nacimiento):
    """
    Calcula la edad en días desde una fecha de nacimiento.
    """
    if not fecha_nacimiento:
        return None
    return (timezone.now().date() - fecha_nacimiento).days


def formatear_numero(numero, decimales=2):
    """
    Formatea un número con separadores de miles y decimales.
    """
    if numero is None:
        return '0'
    return f"{numero:,.{decimales}f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def calcular_conversion_alimenticia(consumo_alimento, ganancia_peso):
    """
    Calcula la conversión alimenticia (kg alimento / kg ganancia peso).
    """
    if ganancia_peso <= 0:
        return None
    return round(consumo_alimento / ganancia_peso, 2)


def generar_codigo_lote(prefijo, fecha):
    """
    Genera un código único para un lote basado en prefijo y fecha.
    """
    fecha_str = fecha.strftime('%Y%m%d')
    return f"{prefijo}-{fecha_str}"


class CalculadoraCostos:
    """
    Clase utilitaria para cálculos de costos en la granja.
    """
    
    @staticmethod
    def costo_por_animal(costo_total, numero_animales):
        """Calcula el costo por animal."""
        if numero_animales <= 0:
            return Decimal('0')
        return round(Decimal(costo_total) / Decimal(numero_animales), 2)
    
    @staticmethod
    def costo_por_kg_producido(costo_total, kg_producidos):
        """Calcula el costo por kg producido."""
        if kg_producidos <= 0:
            return Decimal('0')
        return round(Decimal(costo_total) / Decimal(kg_producidos), 2)
    
    @staticmethod
    def margen_ganancia(precio_venta, costo_produccion):
        """Calcula el margen de ganancia."""
        if costo_produccion <= 0:
            return Decimal('0')
        return round(((Decimal(precio_venta) - Decimal(costo_produccion)) / Decimal(costo_produccion)) * 100, 2)
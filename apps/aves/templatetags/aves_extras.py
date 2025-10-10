from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def format_field_name(field_name):
    """Convierte nombres de campos técnicos a nombres legibles."""
    field_names = {
        'fecha': 'Fecha',
        'semana_vida': 'Semana de Vida',
        'produccion_aaa': 'Producción AAA',
        'produccion_aa': 'Producción AA',
        'produccion_a': 'Producción A',
        'produccion_b': 'Producción B',
        'produccion_c': 'Producción C',
        'mortalidad': 'Mortalidad',
        'causa_mortalidad': 'Causa de Mortalidad',
        'consumo_concentrado': 'Consumo de Concentrado (kg)',
        'observaciones': 'Observaciones',
        'lote': 'Lote',
    }
    return field_names.get(field_name, field_name.replace('_', ' ').title())

@register.filter
def format_field_value(value, field_name):
    """Formatea valores de campos según su tipo."""
    if value is None or value == '' or value == 'None':
        return '<em class="text-muted">Sin valor</em>'
    
    # Campos numéricos
    if field_name in ['produccion_aaa', 'produccion_aa', 'produccion_a', 'produccion_b', 'produccion_c', 'mortalidad']:
        return f'{value} unidades'
    
    # Campo de consumo
    if field_name == 'consumo_concentrado':
        return f'{value} kg'
    
    # Campo de semana
    if field_name == 'semana_vida':
        return f'Semana {value}'
    
    # Campo de fecha
    if field_name == 'fecha':
        try:
            from datetime import datetime
            if isinstance(value, str):
                # Intentar parsear fecha ISO
                if 'T' in value:
                    date_obj = datetime.fromisoformat(value.replace('Z', '+00:00')).date()
                else:
                    date_obj = datetime.fromisoformat(value).date()
                return date_obj.strftime('%d/%m/%Y')
        except:
            pass
    
    return str(value)

@register.filter
def get_change_badge_class(field_name):
    """Retorna la clase CSS para el badge según el tipo de campo."""
    critical_fields = ['mortalidad', 'causa_mortalidad']
    production_fields = ['produccion_aaa', 'produccion_aa', 'produccion_a', 'produccion_b', 'produccion_c']
    
    if field_name in critical_fields:
        return 'badge bg-danger'
    elif field_name in production_fields:
        return 'badge bg-success'
    elif field_name == 'consumo_concentrado':
        return 'badge bg-warning'
    else:
        return 'badge bg-info'

@register.filter
def parse_json_safe(value):
    """Parsea JSON de forma segura."""
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value) if value else {}
    except:
        return {}

@register.filter
def lookup(dictionary, key):
    """Permite acceder a valores de diccionario en templates."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def default_if_none(value, default):
    """Retorna un valor por defecto si el valor es None."""
    return default if value is None else value

@register.filter
def dict_items(dictionary):
    """Convierte un diccionario en una lista de tuplas (key, value)."""
    if isinstance(dictionary, dict):
        return dictionary.items()
    return []
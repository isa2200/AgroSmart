"""
Formularios para el módulo avícola.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import *


class BitacoraDiariaForm(forms.ModelForm):
    """Formulario para bitácora diaria unificada."""
    
    class Meta:
        model = BitacoraDiaria
        fields = [
            'lote', 'fecha', 'semana_vida', 'produccion_aaa', 'produccion_aa', 'produccion_a',
            'produccion_b', 'produccion_c', 'mortalidad', 'causa_mortalidad', 
            'consumo_concentrado', 'observaciones'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lote': forms.Select(attrs={'class': 'form-control'}),
            'semana_vida': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'produccion_aaa': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'produccion_aa': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'produccion_a': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'produccion_b': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'produccion_c': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'mortalidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'causa_mortalidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Enfermedad, Accidente, etc.'}),
            'consumo_concentrado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        lote = cleaned_data.get('lote')
        
        # Validar que no se registre en fechas futuras
        if fecha and fecha > timezone.now().date():
            raise ValidationError("No se puede registrar información en fechas futuras.")
        
        # Validar que si hay mortalidad, debe haber una causa
        mortalidad = cleaned_data.get('mortalidad', 0)
        causa_mortalidad = cleaned_data.get('causa_mortalidad', '').strip()
        
        if mortalidad > 0 and not causa_mortalidad:
            raise ValidationError("Debe especificar la causa de mortalidad cuando hay aves muertas.")
        
        return cleaned_data


class LoteAvesForm(forms.ModelForm):
    """Formulario para pollas de levante."""
    
    class Meta:
        model = LoteAves
        fields = [
            'codigo', 'galpon', 'linea_genetica', 'procedencia', 'numero_aves_inicial',
            'fecha_llegada', 'peso_total_llegada', 'peso_promedio_llegada', 'estado', 'observaciones'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'galpon': forms.TextInput(attrs={'class': 'form-control'}),
            'linea_genetica': forms.Select(attrs={'class': 'form-control'}),
            'procedencia': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_aves_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'fecha_llegada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'peso_total_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'peso_promedio_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['numero_aves_inicial'].widget.attrs['readonly'] = True


class MovimientoHuevosForm(forms.ModelForm):
    """Formulario para movimiento de huevos."""
    
    class Meta:
        model = MovimientoHuevos
        fields = [
            'fecha', 'tipo_movimiento', 'categoria_huevo', 'cantidad',
            'precio_unitario', 'cliente', 'conductor', 'numero_comprobante',
            'observaciones'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_movimiento': forms.Select(attrs={'class': 'form-control'}),
            'categoria_huevo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'conductor': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_comprobante': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        categoria_huevo = cleaned_data.get('categoria_huevo')
        cantidad = cleaned_data.get('cantidad')
        
        # Aplicar reglas de negocio
        if tipo_movimiento == 'venta':
            if categoria_huevo in ['B', 'C']:
                raise ValidationError("Los huevos categoría B y C no pueden venderse, solo autoconsumo.")
        
        # Validar stock disponible
        if categoria_huevo and cantidad:
            try:
                inventario = InventarioHuevos.objects.get(categoria=categoria_huevo)
                if cantidad > inventario.cantidad_actual:
                    raise ValidationError(f"No hay suficiente stock. Disponible: {inventario.cantidad_actual}")
            except InventarioHuevos.DoesNotExist:
                raise ValidationError("No existe inventario para esta categoría.")
        
        return cleaned_data


class ControlConcentradoForm(forms.ModelForm):
    """Formulario para control de concentrados."""
    
    class Meta:
        model = ControlConcentrado
        fields = [
            'tipo_concentrado', 'tipo_movimiento', 'cantidad_kg', 'fecha',
            'lote', 'galpon', 'proveedor', 'numero_factura', 'observaciones'
        ]
        widgets = {
            'tipo_concentrado': forms.Select(attrs={'class': 'form-control'}),
            'tipo_movimiento': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lote': forms.Select(attrs={'class': 'form-control'}),
            'galpon': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PlanVacunacionForm(forms.ModelForm):
    """Formulario para plan de vacunación."""
    
    class Meta:
        model = PlanVacunacion
        fields = [
            'lote', 'tipo_vacuna', 'fecha_programada', 'fecha_aplicada',
            'numero_aves_vacunadas', 'lote_vacuna', 'observaciones', 'aplicada'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-control'}),
            'tipo_vacuna': forms.Select(attrs={'class': 'form-control'}),
            'fecha_programada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_aplicada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'numero_aves_vacunadas': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'lote_vacuna': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'aplicada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JustificacionForm(forms.Form):
    """Formulario para justificaciones de modificaciones."""
    justificacion = forms.CharField(
        label='Justificación de la modificación',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Explique el motivo de la modificación...',
            'required': True
        }),
        max_length=500,
        help_text='Máximo 500 caracteres'
    )
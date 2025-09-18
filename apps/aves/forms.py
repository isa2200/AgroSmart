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
            'fecha_llegada', 'peso_total_llegada', 'peso_promedio_llegada', 'observaciones'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'galpon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Galpón A, Nave 1, etc.'}),
            'linea_genetica': forms.Select(attrs={'class': 'form-control'}),
            'procedencia': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_aves_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'fecha_llegada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'peso_total_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'peso_promedio_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['numero_aves_inicial'].widget.attrs['readonly'] = True
        
        # Hacer el peso promedio de solo lectura ya que se calcula automáticamente
        self.fields['peso_promedio_llegada'].widget.attrs['readonly'] = True
        self.fields['peso_promedio_llegada'].help_text = 'Se calcula automáticamente: (Peso Total × 1000) ÷ Número de Aves'
    
    def clean(self):
        """Validación general y cálculo automático del peso promedio."""
        cleaned_data = super().clean()
        peso_total = cleaned_data.get('peso_total_llegada')
        numero_aves = cleaned_data.get('numero_aves_inicial')
        
        # Calcular peso promedio automáticamente
        if peso_total and numero_aves and numero_aves > 0:
            peso_promedio = (peso_total * 1000) / numero_aves
            cleaned_data['peso_promedio_llegada'] = round(peso_promedio, 2)
        elif peso_total and numero_aves:
            raise ValidationError('No se puede calcular el peso promedio con los datos proporcionados.')
        
        return cleaned_data
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if not codigo:
            raise ValidationError('El código del lote es obligatorio.')
        
        # Verificar que no exista otro lote con el mismo código
        if LoteAves.objects.filter(codigo=codigo.upper()).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('Ya existe un lote con este código.')
        
        return codigo.upper()
    
    def clean_galpon(self):
        galpon = self.cleaned_data.get('galpon')
        if not galpon or not galpon.strip():
            raise ValidationError('El nombre del galpón es obligatorio.')
        return galpon.strip()
    
    def clean_numero_aves_inicial(self):
        numero_aves = self.cleaned_data.get('numero_aves_inicial')
        if not numero_aves or numero_aves <= 0:
            raise ValidationError('El número de aves debe ser mayor a 0.')
        return numero_aves
    
    def clean_peso_total_llegada(self):
        peso_total = self.cleaned_data.get('peso_total_llegada')
        if not peso_total or peso_total <= 0:
            raise ValidationError('El peso total debe ser mayor a 0.')
        return peso_total
    
    def clean_linea_genetica(self):
        linea_genetica = self.cleaned_data.get('linea_genetica')
        if not linea_genetica:
            raise ValidationError('Debe seleccionar una línea genética.')
        return linea_genetica


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
            'lote', 'galpon_destino', 'proveedor', 'numero_factura', 'observaciones'
        ]
        widgets = {
            'tipo_concentrado': forms.Select(attrs={'class': 'form-control'}),
            'tipo_movimiento': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lote': forms.Select(attrs={'class': 'form-control'}),
            'galpon_destino': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Galpón A, Nave 1, etc.'}),
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

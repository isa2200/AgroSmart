"""
Formularios para el módulo avícola.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.forms import formset_factory
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
    """Formulario para lotes de aves."""
    
    class Meta:
        model = LoteAves
        fields = [
            'codigo', 'galpon', 'linea_genetica', 'procedencia', 'numero_aves_inicial',
            'fecha_llegada', 'peso_total_llegada', 'peso_promedio_llegada', 'estado', 'observaciones'
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
            'estado': forms.Select(attrs={'class': 'form-control'}),
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


class LoteAvesEditForm(forms.ModelForm):
    """Formulario para editar lotes de aves con justificación obligatoria."""
    
    justificacion = forms.CharField(
        label='Justificación de la modificación',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Explique detalladamente el motivo de la modificación...',
            'required': True
        }),
        help_text='Este campo es obligatorio para registrar cualquier modificación.',
        min_length=10,
        error_messages={
            'required': 'La justificación de la modificación es obligatoria.',
            'min_length': 'La justificación debe tener al menos 10 caracteres.'
        }
    )
    
    class Meta:
        model = LoteAves
        fields = [
            'codigo', 'galpon', 'linea_genetica', 'procedencia', 'numero_aves_inicial',
            'numero_aves_actual', 'fecha_llegada', 'peso_total_llegada', 
            'peso_promedio_llegada', 'estado', 'fecha_inicio_postura', 'observaciones'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'galpon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Galpón A, Nave 1, etc.'}),
            'linea_genetica': forms.Select(attrs={'class': 'form-control'}),
            'procedencia': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_aves_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'readonly': True}),
            'numero_aves_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fecha_llegada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'peso_total_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'peso_promedio_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio_postura': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        help_texts = {
            'numero_aves_inicial': 'Este campo no se puede modificar después de la creación.',
            'numero_aves_actual': 'Número actual de aves vivas en el lote.',
            'fecha_inicio_postura': 'Solo para lotes en estado de postura.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer que algunos campos sean de solo lectura si el lote ya existe
        if self.instance and self.instance.pk:
            self.fields['numero_aves_inicial'].widget.attrs['readonly'] = True
            self.fields['codigo'].widget.attrs['readonly'] = True
    
    def clean_numero_aves_actual(self):
        numero_aves_actual = self.cleaned_data.get('numero_aves_actual')
        numero_aves_inicial = self.instance.numero_aves_inicial if self.instance else 0
        
        if numero_aves_actual > numero_aves_inicial:
            raise forms.ValidationError(
                f'El número de aves actual ({numero_aves_actual}) no puede ser mayor '
                f'al número inicial ({numero_aves_inicial}).'
            )
        
        if numero_aves_actual < 0:
            raise forms.ValidationError('El número de aves actual no puede ser negativo.')
        
        return numero_aves_actual
    
    def clean_fecha_inicio_postura(self):
        fecha_inicio_postura = self.cleaned_data.get('fecha_inicio_postura')
        estado = self.cleaned_data.get('estado')
        fecha_llegada = self.cleaned_data.get('fecha_llegada') or (self.instance.fecha_llegada if self.instance else None)
        
        if estado == 'postura' and not fecha_inicio_postura:
            raise forms.ValidationError('La fecha de inicio de postura es obligatoria para lotes en estado de postura.')
        
        if fecha_inicio_postura and fecha_llegada and fecha_inicio_postura < fecha_llegada:
            raise forms.ValidationError('La fecha de inicio de postura no puede ser anterior a la fecha de llegada.')
        
        return fecha_inicio_postura
    
    def clean_justificacion(self):
        justificacion = self.cleaned_data.get('justificacion', '').strip()
        if not justificacion:
            raise forms.ValidationError('La justificación de la modificación es obligatoria.')
        if len(justificacion) < 10:
            raise forms.ValidationError('La justificación debe tener al menos 10 caracteres.')
        return justificacion


class MovimientoHuevosForm(forms.ModelForm):
    """Formulario para el encabezado del movimiento de huevos."""
    
    class Meta:
        model = MovimientoHuevos
        fields = [
            'fecha', 'tipo_movimiento', 'cliente', 'conductor', 
            'numero_comprobante', 'observaciones'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_movimiento': forms.Select(attrs={'class': 'form-control'}),
            'cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'conductor': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_comprobante': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha > timezone.now().date():
            raise ValidationError("No se puede registrar movimientos en fechas futuras.")
        return fecha


class DetalleMovimientoHuevosForm(forms.ModelForm):
    """Formulario para cada detalle del movimiento de huevos."""
    
    class Meta:
        model = DetalleMovimientoHuevos
        fields = ['categoria_huevo', 'cantidad_docenas', 'precio_por_docena']
        widgets = {
            'categoria_huevo': forms.Select(attrs={
                'class': 'form-control categoria-select'
            }),
            'cantidad_docenas': forms.NumberInput(attrs={
                'class': 'form-control cantidad-input',
                'step': '0.01',
                'min': '0.01'
            }),
            'precio_por_docena': forms.NumberInput(attrs={
                'class': 'form-control precio-input',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar choices para categoria_huevo
        self.fields['categoria_huevo'].choices = [('', '---------')] + list(MovimientoHuevos.CATEGORIAS_HUEVO)
        
        # Hacer campos requeridos
        self.fields['categoria_huevo'].required = True
        self.fields['cantidad_docenas'].required = True
        
        # Configurar labels más descriptivos
        self.fields['cantidad_docenas'].label = 'Cantidad (docenas)'
        self.fields['precio_por_docena'].label = 'Precio por docena'
        
        # Configurar help_text
        self.fields['cantidad_docenas'].help_text = 'Ingrese la cantidad en docenas (12 unidades por docena)'
        self.fields['precio_por_docena'].help_text = 'Precio por cada docena de huevos'

    def clean_categoria_huevo(self):
        categoria = self.cleaned_data.get('categoria_huevo')
        if not categoria:
            raise ValidationError("La categoría de huevo es requerida.")
        return categoria

    def clean_cantidad_docenas(self):
        cantidad = self.cleaned_data.get('cantidad_docenas')
        if cantidad is None or cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad

    def clean_precio_por_docena(self):
        precio = self.cleaned_data.get('precio_por_docena')
        if precio is not None and precio < 0:
            raise ValidationError("El precio no puede ser negativo.")
        return precio

    def clean(self):
        cleaned_data = super().clean()
        # Las validaciones específicas del modelo se manejan en el método clean() del modelo
        return cleaned_data


# Crear el formset para manejar múltiples detalles
DetalleMovimientoHuevosFormSet = formset_factory(
    DetalleMovimientoHuevosForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


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


class BitacoraDiariaEditForm(forms.ModelForm):
    """Formulario para editar bitácora diaria con justificación obligatoria."""
    
    justificacion = forms.CharField(
        label='Justificación de la modificación',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Explique detalladamente el motivo de la modificación...',
            'required': True
        }),
        help_text='Este campo es obligatorio para registrar cualquier modificación.',
        min_length=10,
        error_messages={
            'required': 'La justificación de la modificación es obligatoria.',
            'min_length': 'La justificación debe tener al menos 10 caracteres.'
        }
    )
    
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
    
    def clean_justificacion(self):
        justificacion = self.cleaned_data.get('justificacion', '').strip()
        if not justificacion:
            raise forms.ValidationError('La justificación de la modificación es obligatoria.')
        if len(justificacion) < 10:
            raise forms.ValidationError('La justificación debe tener al menos 10 caracteres.')
        return justificacion


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

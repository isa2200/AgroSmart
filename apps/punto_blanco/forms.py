from django import forms
from django.core.exceptions import ValidationError
from .models import Pedido, DetallePedido, ConfiguracionPuntoBlanco
from apps.aves.models import InventarioHuevos


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'cliente_nombre', 'cliente_telefono', 'cliente_email', 
            'cliente_direccion', 'tipo_entrega', 'fecha_entrega_estimada', 
            'observaciones'
        ]
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cliente_direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_entrega': forms.Select(attrs={'class': 'form-control'}),
            'fecha_entrega_estimada': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_cliente_telefono(self):
        telefono = self.cleaned_data.get('cliente_telefono')
        if telefono and len(telefono) < 7:
            raise ValidationError('El teléfono debe tener al menos 7 dígitos')
        return telefono


class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['inventario_huevos', 'cantidad', 'precio_unitario']
        widgets = {
            'inventario_huevos': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'precio_unitario': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar inventarios con stock disponible
        self.fields['inventario_huevos'].queryset = InventarioHuevos.objects.filter(
            cantidad_actual__gt=0
        )
    
    def clean(self):
        cleaned_data = super().clean()
        inventario = cleaned_data.get('inventario_huevos')
        cantidad = cleaned_data.get('cantidad')
        
        if inventario and cantidad:
            if cantidad > inventario.cantidad_actual:
                raise ValidationError(
                    f'No hay suficiente stock de {inventario.categoria}. '
                    f'Disponible: {inventario.cantidad_actual}'
                )
        
        return cleaned_data


class ConfiguracionPuntoBlancoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionPuntoBlanco
        fields = '__all__'
        widgets = {
            'nombre_punto': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'margen_ganancia_default': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'hora_apertura': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_cierre': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'costo_domicilio': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'radio_entrega_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Formset para manejar múltiples detalles de pedido
DetallePedidoFormSet = forms.inlineformset_factory(
    Pedido,
    DetallePedido,
    form=DetallePedidoForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
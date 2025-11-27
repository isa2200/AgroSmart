from django import forms
from .models import LotePorcino, BitacoraDiariaPorcinos


class LotePorcinoForm(forms.ModelForm):
    class Meta:
        model = LotePorcino
        fields = [
            'codigo', 'corral', 'procedencia', 'numero_cerdos_inicial',
            'numero_cerdos_actual', 'fecha_llegada', 'peso_total_llegada',
            'peso_promedio_llegada', 'estado', 'observaciones'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'corral': forms.TextInput(attrs={'class': 'form-control'}),
            'procedencia': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_cerdos_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'numero_cerdos_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fecha_llegada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'peso_total_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'peso_promedio_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BitacoraDiariaPorcinosForm(forms.ModelForm):
    class Meta:
        model = BitacoraDiariaPorcinos
        fields = [
            'lote', 'fecha', 'peso_promedio', 'consumo_alimento_kg',
            'animales_enfermos', 'mortalidad', 'tratamiento_aplicado', 'observaciones'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'peso_promedio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'consumo_alimento_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'animales_enfermos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'mortalidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'tratamiento_aplicado': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

from django import forms
from .models import InventarioConejos, LibroDiarioConejos

class InventarioConejosForm(forms.ModelForm):
    class Meta:
        model = InventarioConejos
        fields = [
            'fecha', 'detalle', 'madre_id',
            'gazapos_vivos', 'gazapos_muertos', 'compra', 'venta', 'muerte',
            'macho_levante_ceba', 'hembra_levante_ceba', 'reproductores',
            'hembra_reemplazo', 'hembra_no_lactando', 'hembra_lactando', 'gazapos'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'detalle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Parto Jaula #38'}),
            'madre_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Madre'}),
            
            # Novedades
            'gazapos_vivos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'gazapos_muertos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'compra': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'venta': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'muerte': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            
            # Inventario
            'macho_levante_ceba': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'hembra_levante_ceba': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reproductores': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'hembra_reemplazo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'hembra_no_lactando': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'hembra_lactando': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'gazapos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class LibroDiarioConejosForm(forms.ModelForm):
    class Meta:
        model = LibroDiarioConejos
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Partos
            'parto_jaula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Jaula'}),
            'parto_vivos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'parto_muertos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            
            # Palpación
            'palpacion_jaula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Jaula'}),
            'palpacion_estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado'}),
            
            # Montas
            'monta_jaula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Jaula'}),
            'monta_macho': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Macho'}),
            
            # Muertes
            'muerte_jaula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Jaula'}),
            'muerte_gazapos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'muerte_levante_ceba': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'muerte_reproductores': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            
            # Ventas
            'venta_jaula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Jaula'}),
            'venta_levante_ceba': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'venta_pie_cria': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            
            # Manejo Gazapera
            'gazapera_poner_jaula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Poner Jaula'}),
            'gazapera_quitar_jaula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quitar Jaula'}),
            
            # Destetes
            'destete_jaula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro Jaula'}),
            'destete_cantidad_hembras': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'destete_cantidad_machos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'destete_peso_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            
            # Otros
            'tratamientos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Tratamientos'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observaciones'}),
            
            # Alimentación
            'alimentacion_levante_ceba': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'alimentacion_reproduccion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'alimentacion_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

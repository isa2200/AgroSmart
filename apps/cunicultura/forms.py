from django import forms
from .models import InventarioConejos, LibroDiarioConejos, ControlDestetes, RegistroAlimentoConejos, BitacoraActividadesConejos, TareaCunicultura

class InventarioConejosForm(forms.ModelForm):
    class Meta:
        model = InventarioConejos
        fields = [
            'fecha', 'detalle', 'madre_id',
            'gazapos_vivos', 'gazapos_muertos', 'compra', 'venta', 'muerte',
            'macho_levante_ceba', 'hembra_levante_ceba', 'reproductores',
            'hembra_reemplazo', 'hembra_no_lactando', 'hembra_lactando', 'gazapos',
            'firma_responsable'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'detalle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Parto Jaula #38'}),
            'madre_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Madre'}),
            'firma_responsable': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            
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

from .models import PlanVacunacion

class PlanVacunacionForm(forms.ModelForm):
    class Meta:
        model = PlanVacunacion
        fields = ['fecha_programada', 'nombre_vacuna', 'detalle', 'fecha_aplicada', 'aplicada', 'observaciones']
        widgets = {
            'fecha_programada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre_vacuna': forms.TextInput(attrs={'class': 'form-control'}),
            'detalle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Jaula 5, Lote 2'}),
            'fecha_aplicada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'aplicada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ControlDestetesForm(forms.ModelForm):
    class Meta:
        model = ControlDestetes
        fields = '__all__'
        widgets = {
            'camada_numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 871'}),
            'numero_animales': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'hembras_cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'hembras_peso_promedio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'machos_cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'machos_peso_promedio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'madre_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'padre_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_destete': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
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
            'alimentacion_am': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'AM'}),
            'alimentacion_pm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'PM'}),
            'alimentacion_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
        }

class RegistroAlimentoConejosForm(forms.ModelForm):
    class Meta:
        model = RegistroAlimentoConejos
        fields = ['fecha', 'unidad', 'entrada', 'salida']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kg, Bultos, etc.'}),
            'entrada': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'salida': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }

class BitacoraActividadesConejosForm(forms.ModelForm):
    class Meta:
        model = BitacoraActividadesConejos
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actividad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TareaCuniculturaForm(forms.ModelForm):
    class Meta:
        model = TareaCunicultura
        fields = ['titulo', 'prioridad', 'fecha_limite', 'responsable', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la tarea'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'fecha_limite': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada'}),
        }

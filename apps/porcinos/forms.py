from django import forms
from .models import LotePorcino, BitacoraDiariaPorcinos, AlertaPorcinos, TareaPorcinos, AnimalPorcino, InventarioPorcino, PlanVacunacion

class LotePorcinoForm(forms.ModelForm):
    class Meta:
        model = LotePorcino
        fields = ['codigo', 'corral', 'procedencia', 'numero_cerdos_inicial', 'fecha_llegada', 'peso_promedio_llegada', 'observaciones']
        widgets = {
            'fecha_llegada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'corral': forms.TextInput(attrs={'class': 'form-control'}),
            'procedencia': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_cerdos_inicial': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso_promedio_llegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BitacoraDiariaPorcinosForm(forms.ModelForm):
    class Meta:
        model = BitacoraDiariaPorcinos
        fields = ['fecha', 'lote', 'peso_promedio', 'consumo_alimento_kg', 'animales_enfermos', 'mortalidad', 'tratamiento_aplicado', 'observaciones', 'firma_encargado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'peso_promedio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'consumo_alimento_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'animales_enfermos': forms.NumberInput(attrs={'class': 'form-control'}),
            'mortalidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'tratamiento_aplicado': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'firma_encargado': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AnimalPorcinoForm(forms.ModelForm):
    class Meta:
        model = AnimalPorcino
        fields = ['codigo', 'nombre', 'fecha_nacimiento', 'raza', 'sexo', 'etapa', 'peso_actual', 'lote', 'foto', 'notas']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'raza': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'etapa': forms.Select(attrs={'class': 'form-select'}),
            'peso_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TareaPorcinosForm(forms.ModelForm):
    class Meta:
        model = TareaPorcinos
        fields = ['titulo', 'descripcion', 'prioridad', 'fecha_limite', 'responsable']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la tarea'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'fecha_limite': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }

class PlanVacunacionForm(forms.ModelForm):
    class Meta:
        model = PlanVacunacion
        fields = ['fecha_programada', 'nombre_vacuna', 'lote', 'fecha_aplicada', 'aplicada', 'observaciones']
        widgets = {
            'fecha_programada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre_vacuna': forms.TextInput(attrs={'class': 'form-control'}),
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'fecha_aplicada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'aplicada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

from django import forms
from .models import Tarea, Equino, RegistroDiario

class EquinoForm(forms.ModelForm):
    class Meta:
        model = Equino
        fields = ['nombre', 'raza', 'fecha_nacimiento', 'sexo', 'color', 'microchip', 
                 'padre', 'madre', 'estado', 'foto', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del equino'}),
            'raza': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Raza'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Color/Pelaje'}),
            'microchip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de microchip'}),
            'padre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del padre'}),
            'madre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la madre'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales'}),
        }

class RegistroDiarioForm(forms.ModelForm):
    class Meta:
        model = RegistroDiario
        fields = ['fecha', 'actividad', 'observaciones', 'responsable']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actividad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del registro'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contexto del día, actividades realizadas, observaciones...'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'prioridad', 'fecha_limite', 'responsable']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la tarea'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'fecha_limite': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }

from .models import PlanVacunacion

class PlanVacunacionForm(forms.ModelForm):
    class Meta:
        model = PlanVacunacion
        fields = ['equino', 'fecha_programada', 'nombre_vacuna', 'fecha_aplicada', 'aplicada', 'observaciones']
        widgets = {
            'equino': forms.Select(attrs={'class': 'form-select'}),
            'fecha_programada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nombre_vacuna': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_aplicada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'aplicada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

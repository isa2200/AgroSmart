from django import forms
from django.contrib.auth.models import User
from .models import TipoReporte, ReporteProgramado
from apps.core.models import Lote, Categoria

class FiltroReporteForm(forms.Form):
    """
    Formulario para filtros de reportes
    """
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha Inicio'
    )
    
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha Fin'
    )
    
    tipo_animal = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('aves', 'Aves'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Animal'
    )
    
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.filter(estado='activo'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Lote',
        empty_label='Todos los lotes'
    )
    
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(estado='activo'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Categoría',
        empty_label='Todas las categorías'
    )
    
    formato_salida = forms.ChoiceField(
        choices=[
            ('excel', 'Excel'),
            ('csv', 'CSV')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Formato de Salida',
        initial='excel'
    )
    
    incluir_graficos = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Incluir Gráficos'
    )

class ReporteProgramadoForm(forms.ModelForm):
    """
    Formulario para crear reportes programados
    """
    emails_destino_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ingrese emails separados por comas'
        }),
        label='Emails de Destino',
        help_text='Separe múltiples emails con comas'
    )
    
    class Meta:
        model = ReporteProgramado
        fields = [
            'nombre', 'descripcion', 'tipo_reporte', 'frecuencia',
            'hora_ejecucion', 'dia_semana', 'dia_mes', 'formato_salida',
            'enviar_email'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'tipo_reporte': forms.Select(attrs={'class': 'form-select'}),
            'frecuencia': forms.Select(attrs={'class': 'form-select'}),
            'hora_ejecucion': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'dia_semana': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 7
            }),
            'dia_mes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 31
            }),
            'formato_salida': forms.Select(attrs={'class': 'form-select'}),
            'enviar_email': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def clean_emails_destino_text(self):
        emails_text = self.cleaned_data.get('emails_destino_text', '')
        if emails_text:
            emails = [email.strip() for email in emails_text.split(',')]
            # Validar formato de emails
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            
            for email in emails:
                try:
                    validate_email(email)
                except ValidationError:
                    raise forms.ValidationError(f'Email inválido: {email}')
            
            return emails
        return []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.emails_destino = self.cleaned_data.get('emails_destino_text', [])
        
        if commit:
            instance.save()
        return instance

class ReportePersonalizadoForm(forms.Form):
    """
    Formulario para crear reportes personalizados
    """
    nombre_reporte = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del reporte personalizado'
        })
    )
    
    modelo_base = forms.ChoiceField(
        choices=[
            ('aves', 'Aves'),
            ('produccion', 'Producción General')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Modelo Base'
    )
    
    campos_incluir = forms.MultipleChoiceField(
        choices=[],  # Se llenarán dinámicamente
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Campos a Incluir'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campos disponibles según el modelo
        campos_opciones = {
            'aves': [
                ('identificacion', 'Identificación'),
                ('linea', 'Línea'),
                ('sexo', 'Sexo'),
                ('fecha_nacimiento', 'Fecha de Nacimiento'),
                ('peso_inicial', 'Peso Inicial')
            ],
        }
"""
Formularios para la gestión de gallinas ponedoras en AgroSmart.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from .models import (
    LoteAves, ProduccionHuevos, CostosProduccion, 
    Vacunacion, CalendarioVacunas, Mortalidad,
)


class LoteAvesForm(forms.ModelForm):
    """
    Formulario para crear y editar lotes de aves.
    """
    class Meta:
        model = LoteAves
        fields = [
            'codigo', 'nombre_lote', 'linea', 'fecha_inicio', 'fecha_fin_produccion',
            'cantidad_aves', 'cantidad_actual', 'costo_ave_inicial', 'estado', 'observaciones'
        ]

        widgets = {
            'nombre_lote': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Lote A-2024-01'
            }),
            'linea': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cantidad_aves': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Número de aves inicial'
            }),
            'cantidad_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Número de aves actual'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: LOT-2024-001'
            }),
            'fecha_fin_produccion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'costo_ave_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Costo por ave'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Información del Lote',
                Row(
                    Column('nombre_lote', css_class='form-group col-md-6 mb-3'),
                    Column('linea', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('fecha_inicio', css_class='form-group col-md-4 mb-3'),
                    Column('cantidad_aves', css_class='form-group col-md-4 mb-3'),
                    Column('cantidad_actual', css_class='form-group col-md-4 mb-3'),
                ),
                Row(
                    Column('estado', css_class='form-group col-md-6 mb-3'),
                ),
                'observaciones'
            ),
            FormActions(
                Submit('submit', 'Guardar Lote', css_class='btn btn-primary'),
                HTML('<a href="{% url "aves:lote_list" %}" class="btn btn-secondary ms-2">Cancelar</a>')
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        cantidad_aves = cleaned_data.get('cantidad_aves')
        cantidad_actual = cleaned_data.get('cantidad_actual')
        
        if cantidad_actual and cantidad_aves and cantidad_actual > cantidad_aves:
            raise ValidationError('La cantidad actual no puede ser mayor a la cantidad inicial.')
        
        return cleaned_data


class ProduccionHuevosForm(forms.ModelForm):
    """
    Formulario para registrar producción diaria de huevos.
    """
    class Meta:
        model = ProduccionHuevos
        fields = [
            'lote', 'fecha', 'semana_produccion', 'yumbos', 'extra', 'aa', 'a', 'b', 'c',
            'pipo', 'sucios', 'totiados', 'yema', 'peso_promedio_huevo', 
            'numero_aves_produccion', 'observaciones'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'semana_produccion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'peso_promedio_huevo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Gramos'
            }),
            'numero_aves_produccion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo lotes activos
        self.fields['lote'].queryset = LoteAves.objects.filter(estado='activo')
        
        # Helper para mejor UX
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Información General',
                Row(
                    Column('lote', css_class='form-group col-md-4 mb-3'),
                    Column('fecha', css_class='form-group col-md-4 mb-3'),
                    Column('semana_produccion', css_class='form-group col-md-4 mb-3'),
                )
            ),
            Fieldset(
                'Clasificación de Huevos',
                HTML('<div class="row">'),
                HTML('<div class="col-md-6">'),
                HTML('<h6 class="text-primary">Huevos Comerciales</h6>'),
                Row(
                    Column('yumbos', css_class='form-group col-md-6 mb-2'),
                    Column('extra', css_class='form-group col-md-6 mb-2'),
                ),
                Row(
                    Column('aa', css_class='form-group col-md-6 mb-2'),
                    Column('a', css_class='form-group col-md-6 mb-2'),
                ),
                Row(
                    Column('b', css_class='form-group col-md-6 mb-2'),
                    Column('c', css_class='form-group col-md-6 mb-2'),
                ),
                HTML('</div>'),
                HTML('<div class="col-md-6">'),
                HTML('<h6 class="text-warning">Huevos No Comerciales</h6>'),
                Row(
                    Column('pipo', css_class='form-group col-md-6 mb-2'),
                    Column('sucios', css_class='form-group col-md-6 mb-2'),
                ),
                Row(
                    Column('totiados', css_class='form-group col-md-6 mb-2'),
                    Column('yema', css_class='form-group col-md-6 mb-2'),
                ),
                HTML('</div>'),
                HTML('</div>'),
            ),
            Fieldset(
                'Datos Adicionales',
                Row(
                    Column('peso_promedio_huevo', css_class='form-group col-md-6 mb-3'),
                    Column('numero_aves_produccion', css_class='form-group col-md-6 mb-3'),
                ),
                'observaciones'
            ),
            FormActions(
                Submit('submit', 'Registrar Producción', css_class='btn btn-success'),
                HTML('<a href="{% url "aves:produccion_list" %}" class="btn btn-secondary ms-2">Cancelar</a>')
            )
        )


class CostosProduccionForm(forms.ModelForm):
    """
    Formulario para registrar costos e ingresos de producción.
    """
    class Meta:
        model = CostosProduccion
        fields = [
            'lote', 'fecha', 'periodo', 'costos_fijos', 'costos_variables',
            'gastos_administracion', 'costo_alimento', 'costo_mano_obra', 'otros_costos',
            'ingresos_venta_huevos', 'ingresos_venta_aves', 'otros_ingresos', 'observaciones'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'periodo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Semana 1, Mes 1'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lote'].queryset = LoteAves.objects.filter(estado='activo')
        
        # Agregar clases CSS a campos monetarios
        money_fields = [
            'costos_fijos', 'costos_variables', 'gastos_administracion',
            'costo_alimento', 'costo_mano_obra', 'otros_costos',
            'ingresos_venta_huevos', 'ingresos_venta_aves', 'otros_ingresos'
        ]
        for field in money_fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            })
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Información General',
                Row(
                    Column('lote', css_class='form-group col-md-4 mb-3'),
                    Column('fecha', css_class='form-group col-md-4 mb-3'),
                    Column('periodo', css_class='form-group col-md-4 mb-3'),
                )
            ),
            Fieldset(
                'Costos de Producción',
                Row(
                    Column('costos_fijos', css_class='form-group col-md-6 mb-3'),
                    Column('costos_variables', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('gastos_administracion', css_class='form-group col-md-6 mb-3'),
                    Column('costo_alimento', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('costo_mano_obra', css_class='form-group col-md-6 mb-3'),
                    Column('otros_costos', css_class='form-group col-md-6 mb-3'),
                )
            ),
            Fieldset(
                'Ingresos',
                Row(
                    Column('ingresos_venta_huevos', css_class='form-group col-md-4 mb-3'),
                    Column('ingresos_venta_aves', css_class='form-group col-md-4 mb-3'),
                    Column('otros_ingresos', css_class='form-group col-md-4 mb-3'),
                )
            ),
            'observaciones',
            FormActions(
                Submit('submit', 'Registrar Costos', css_class='btn btn-primary'),
                HTML('<a href="{% url "aves:costos_list" %}" class="btn btn-secondary ms-2">Cancelar</a>')
            )
        )
    def clean(self):
        cleaned_data = super().clean()
        lote = cleaned_data.get('lote')
        fecha = cleaned_data.get('fecha')
        
        # agregado por corrección QA - Validación costos no negativos
        campos_costo = [
            'costos_fijos', 'costos_variables', 'gastos_administracion',
            'costo_alimento', 'costo_mano_obra', 'otros_costos'
        ]
        
        for campo in campos_costo:
            valor = cleaned_data.get(campo)
            if valor and valor < 0:
                raise ValidationError(f'{campo.replace("_", " ").title()} no puede ser negativo')
        
        # Validar que al menos un costo sea mayor a 0
        total_costos = sum([cleaned_data.get(campo, 0) for campo in campos_costo])
        if total_costos == 0:
            raise ValidationError('Debe ingresar al menos un costo mayor a 0')
        
        # Validar fecha no futura
        if fecha and fecha > timezone.now().date():
            raise ValidationError('No se pueden registrar costos para fechas futuras')
        
        # Validar fecha no anterior al inicio del lote
        if lote and fecha and fecha < lote.fecha_inicio:
            raise ValidationError(
                f'La fecha no puede ser anterior al inicio del lote ({lote.fecha_inicio})'
            )
        
        return cleaned_data


class CalendarioVacunasForm(forms.ModelForm):
    """
    Formulario para crear calendario de vacunación.
    """
    class Meta:
        model = CalendarioVacunas
        fields = [
            'nombre_vacuna', 'dias_post_nacimiento', 'descripcion',
            'dosis_ml', 'via_aplicacion', 'obligatoria'
        ]
        widgets = {
            'nombre_vacuna': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Newcastle, Bronquitis'
            }),
            'dias_post_nacimiento': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'dosis_ml': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'via_aplicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ocular, Subcutánea, Agua de bebida'
            }),
            'obligatoria': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Información de la Vacuna',
                Row(
                    Column('nombre_vacuna', css_class='form-group col-md-6 mb-3'),
                    Column('dias_post_nacimiento', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('dosis_ml', css_class='form-group col-md-6 mb-3'),
                    Column('via_aplicacion', css_class='form-group col-md-6 mb-3'),
                ),
                Div(
                    'obligatoria',
                    css_class='form-check mb-3'
                ),
                'descripcion'
            ),
            FormActions(
                Submit('submit', 'Guardar Vacuna', css_class='btn btn-success'),
                HTML('<a href="{% url "aves:calendario_list" %}" class="btn btn-secondary ms-2">Cancelar</a>')
            )
        )
    def clean(self):  # agregado por corrección QA
        cleaned_data = super().clean()
        dias_post_nacimiento = cleaned_data.get('dias_post_nacimiento')
        dosis_ml = cleaned_data.get('dosis_ml')
        
        # Validar días post-nacimiento razonables
        if dias_post_nacimiento and dias_post_nacimiento > 365:
            raise ValidationError('Los días post-nacimiento no pueden exceder 365 días')
        
        # Validar dosis razonable
        if dosis_ml and dosis_ml > 10:
            raise ValidationError('La dosis no puede exceder 10ml por ave')
        
        return cleaned_data


class VacunacionForm(forms.ModelForm):
    """
    Formulario para registrar vacunaciones aplicadas.
    """
    class Meta:
        model = Vacunacion
        fields = [
            'lote', 'calendario_vacuna', 'fecha_programada', 'fecha_aplicacion',
            'dosis_aplicada', 'numero_aves_vacunadas', 'responsable',
            'lote_vacuna', 'estado', 'observaciones'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'calendario_vacuna': forms.Select(attrs={'class': 'form-select'}),
            'fecha_programada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_aplicacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'dosis_aplicada': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'numero_aves_vacunadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del responsable'
            }),
            'lote_vacuna': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lote de la vacuna'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lote'].queryset = LoteAves.objects.filter(estado='activo')
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Información de Vacunación',
                Row(
                    Column('lote', css_class='form-group col-md-6 mb-3'),
                    Column('calendario_vacuna', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('fecha_programada', css_class='form-group col-md-6 mb-3'),
                    Column('fecha_aplicacion', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('dosis_aplicada', css_class='form-group col-md-4 mb-3'),
                    Column('numero_aves_vacunadas', css_class='form-group col-md-4 mb-3'),
                    Column('estado', css_class='form-group col-md-4 mb-3'),
                ),
                Row(
                    Column('responsable', css_class='form-group col-md-6 mb-3'),
                    Column('lote_vacuna', css_class='form-group col-md-6 mb-3'),
                ),
                'observaciones'
            ),
            FormActions(
                Submit('submit', 'Registrar Vacunación', css_class='btn btn-success'),
                HTML('<a href="{% url "aves:vacunacion_list" %}" class="btn btn-secondary ms-2">Cancelar</a>')
            )
        )
    def clean(self):
        cleaned_data = super().clean()
        lote = cleaned_data.get('lote')
        numero_aves_vacunadas = cleaned_data.get('numero_aves_vacunadas')
        fecha_programada = cleaned_data.get('fecha_programada')
        fecha_aplicacion = cleaned_data.get('fecha_aplicacion')
        dosis_aplicada = cleaned_data.get('dosis_aplicada')
        calendario_vacuna = cleaned_data.get('calendario_vacuna')
        
        # agregado por corrección QA - Validaciones de vacunación
        if lote and numero_aves_vacunadas:
            if numero_aves_vacunadas > lote.cantidad_actual:
                raise ValidationError(
                    f'No se pueden vacunar más aves ({numero_aves_vacunadas}) '
                    f'que las disponibles en el lote ({lote.cantidad_actual})'
                )
        
        # Validar fecha de aplicación no anterior a programada
        if fecha_programada and fecha_aplicacion:
            if fecha_aplicacion < fecha_programada:
                raise ValidationError(
                    'La fecha de aplicación no puede ser anterior a la fecha programada'
                )
        
        # Validar dosis aplicada vs dosis recomendada
        if calendario_vacuna and dosis_aplicada:
            dosis_recomendada = calendario_vacuna.dosis_ml
            if dosis_aplicada > (dosis_recomendada * 1.5):
                raise ValidationError(
                    f'La dosis aplicada ({dosis_aplicada}ml) excede significativamente '
                    f'la dosis recomendada ({dosis_recomendada}ml)'
                )
        
        return cleaned_data


class MortalidadForm(forms.ModelForm):
    """
    Formulario para registrar mortalidad.
    """
    class Meta:
        model = Mortalidad
        fields = [
            'lote', 'fecha', 'cantidad_muertas', 'causa',
            'descripcion_causa', 'accion_tomada'
        ]
        widgets = {
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cantidad_muertas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'causa': forms.Select(attrs={'class': 'form-select'}),
            'descripcion_causa': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe la causa de la mortalidad...'
            }),
            'accion_tomada': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe las acciones tomadas...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lote'].queryset = LoteAves.objects.filter(estado='activo')
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Registro de Mortalidad',
                Row(
                    Column('lote', css_class='form-group col-md-4 mb-3'),
                    Column('fecha', css_class='form-group col-md-4 mb-3'),
                    Column('cantidad_muertas', css_class='form-group col-md-4 mb-3'),
                ),
                'causa',
                'descripcion_causa',
                'accion_tomada'
            ),
            FormActions(
                Submit('submit', 'Registrar Mortalidad', css_class='btn btn-danger'),
                HTML('<a href="{% url "aves:mortalidad_list" %}" class="btn btn-secondary ms-2">Cancelar</a>')
            )
        )


class FiltroProduccionForm(forms.Form):
    """
    Formulario para filtrar reportes de producción.
    """
    lote = forms.ModelChoiceField(
        queryset=LoteAves.objects.filter(estado='activo'),
        required=False,
        empty_label='Todos los lotes',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('lote', css_class='form-group col-md-4 mb-3'),
                Column('fecha_inicio', css_class='form-group col-md-4 mb-3'),
                Column('fecha_fin', css_class='form-group col-md-4 mb-3'),
            ),
            FormActions(
                Submit('submit', 'Filtrar', css_class='btn btn-primary'),
                HTML('<a href="." class="btn btn-secondary ms-2">Limpiar</a>')
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        lote = cleaned_data.get('lote')
        fecha = cleaned_data.get('fecha')
        numero_aves_produccion = cleaned_data.get('numero_aves_produccion')
        
        # Validar que no exista registro duplicado para el mismo lote y fecha
        if lote and fecha:
            existing = ProduccionHuevos.objects.filter(
                lote=lote, fecha=fecha
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    f'Ya existe un registro de producción para el lote {lote.nombre_lote} en la fecha {fecha}'
                )
        
        # Validar que el número de aves en producción no exceda la cantidad actual del lote
        if lote and numero_aves_produccion:
            if numero_aves_produccion > lote.cantidad_actual:
                raise ValidationError(
                    f'El número de aves en producción ({numero_aves_produccion}) no puede ser mayor '
                    f'a la cantidad actual del lote ({lote.cantidad_actual})'
                )
        
        # Validar que la fecha no sea futura
        if fecha and fecha > timezone.now().date():
            raise ValidationError('No se puede registrar producción para fechas futuras')
        
        # Validar que la fecha no sea anterior al inicio del lote
        if lote and fecha and fecha < lote.fecha_inicio:
            raise ValidationError(
                f'La fecha de producción no puede ser anterior al inicio del lote ({lote.fecha_inicio})'
            )
        
        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        lote = cleaned_data.get('lote')
        fecha = cleaned_data.get('fecha')
        numero_aves_produccion = cleaned_data.get('numero_aves_produccion')
        
        
        # Validar que no exista registro duplicado para el mismo lote y fecha
        if lote and fecha:
            existing = ProduccionHuevos.objects.filter(
                lote=lote, fecha=fecha
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    f'Ya existe un registro de producción para el lote {lote.nombre_lote} en la fecha {fecha}'
                )
        
        # Validar que el número de aves en producción no exceda la cantidad actual del lote
        if lote and numero_aves_produccion:
            if numero_aves_produccion > lote.cantidad_actual:
                raise ValidationError(
                    f'El número de aves en producción ({numero_aves_produccion}) no puede ser mayor '
                    f'a la cantidad actual del lote ({lote.cantidad_actual})'
                )
        
        # Validar que la fecha no sea futura
        if fecha and fecha > timezone.now().date():
            raise ValidationError('No se puede registrar producción para fechas futuras')
        
        # Validar que la fecha no sea anterior al inicio del lote


        if lote and fecha and fecha < lote.fecha_inicio:
            raise ValidationError(
                f'La fecha de producción no puede ser anterior al inicio del lote ({lote.fecha_inicio})'
            )
        
        return cleaned_data



    def clean(self):
        cleaned_data = super().clean()
        lote = cleaned_data.get('lote')
        cantidad_muertas = cleaned_data.get('cantidad_muertas')
        fecha = cleaned_data.get('fecha')
        
        # Validar que la cantidad de muertas no exceda la cantidad actual del lote
        if lote and cantidad_muertas:
            if cantidad_muertas > lote.cantidad_actual:
                raise ValidationError(
                    f'La cantidad de aves muertas ({cantidad_muertas}) no puede ser mayor '
                    f'a la cantidad actual del lote ({lote.cantidad_actual})'
                )
        
        # Validar que la fecha no sea futura
        if fecha and fecha > timezone.now().date():
            raise ValidationError('No se puede registrar mortalidad para fechas futuras')
        
        # Validar que la fecha no sea anterior al inicio del lote
        if lote and fecha and fecha < lote.fecha_inicio:
            raise ValidationError(
                f'La fecha de mortalidad no puede ser anterior al inicio del lote ({lote.fecha_inicio})'
            )
        
        return cleaned_data

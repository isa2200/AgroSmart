"""
Formularios para la gestión de usuarios.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import PerfilUsuario


class RegistroUsuarioForm(UserCreationForm):
    """
    Formulario para registro de nuevos usuarios.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'username',
            'email',
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Registrar Usuario', css_class='btn btn-primary')
        )


class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario.
    """
    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'telefono', 'cedula', 'fecha_nacimiento', 'direccion', 'foto']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'rol',
            Row(
                Column('cedula', css_class='form-group col-md-6 mb-0'),
                Column('telefono', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'fecha_nacimiento',
            'direccion',
            'foto',
            Submit('submit', 'Actualizar Perfil', css_class='btn btn-success')
        )


class LoginForm(AuthenticationForm):
    """
    Formulario personalizado de login.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            HTML('<div class="form-check mb-3"><input class="form-check-input" type="checkbox" id="remember_me"><label class="form-check-label" for="remember_me">Recordarme</label></div>'),
            Submit('submit', 'Iniciar Sesión', css_class='btn btn-primary w-100')
        )
        
        # Personalizar campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
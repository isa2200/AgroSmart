"""
Formularios para la gestión de usuarios.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Div
from .models import PerfilUsuario


class RegistroUsuarioForm(UserCreationForm):
    """
    Formulario para registro de nuevos usuarios.
    """
    email = forms.EmailField(required=True, label='Correo Electrónico')
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


class RegistroCompletoForm(UserCreationForm):
    """
    Formulario completo para registro de nuevos usuarios con perfil y roles.
    """
    # Campos del usuario
    email = forms.EmailField(required=True, label='Correo Electrónico')
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    
    # Campos del perfil
    rol = forms.ChoiceField(
        choices=PerfilUsuario.ROLES,
        required=True,
        label='Rol del Usuario',
        help_text='Selecciona el rol que tendrá el usuario en el sistema'
    )
    telefono = forms.CharField(
        max_length=15, 
        required=False, 
        label='Teléfono',
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 3001234567'})
    )
    cedula = forms.CharField(
        max_length=20, 
        required=False, 
        label='Cédula',
        widget=forms.TextInput(attrs={'placeholder': 'Número de identificación'})
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        label='Fecha de Nacimiento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    direccion = forms.CharField(
        required=False,
        label='Dirección',
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Dirección completa'})
    )
    
    # Permisos específicos
    acceso_modulo_avicola = forms.BooleanField(
        required=False,
        label='Acceso al Módulo Avícola',
        help_text='Permite al usuario acceder al módulo de gestión avícola'
    )
    puede_eliminar_registros = forms.BooleanField(
        required=False,
        label='Puede Eliminar Registros',
        help_text='Permite al usuario eliminar registros del sistema'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4 class="mb-3"><i class="fas fa-user"></i> Información Personal</h4>'),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('cedula', css_class='form-group col-md-6 mb-0'),
                Column('telefono', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'fecha_nacimiento',
            'direccion',
            
            HTML('<hr><h4 class="mb-3"><i class="fas fa-key"></i> Contraseña</h4>'),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            HTML('<hr><h4 class="mb-3"><i class="fas fa-user-tag"></i> Rol y Permisos</h4>'),
            'rol',
            Div(
                'acceso_modulo_avicola',
                'puede_eliminar_registros',
                css_class='border p-3 bg-light rounded'
            ),
            
            HTML('<hr>'),
            Submit('submit', 'Crear Usuario', css_class='btn btn-success btn-lg w-100')
        )
        
        # Personalizar widgets
        self.fields['username'].help_text = 'Nombre único para iniciar sesión'
        self.fields['rol'].widget.attrs.update({'class': 'form-select'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Verificar si ya existe un perfil (creado por el signal)
            try:
                perfil = user.perfilusuario
                # Si existe, actualizar los datos
                perfil.rol = self.cleaned_data['rol']
                perfil.telefono = self.cleaned_data.get('telefono', '')
                perfil.cedula = self.cleaned_data.get('cedula', '')
                perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
                perfil.direccion = self.cleaned_data.get('direccion', '')
                perfil.acceso_modulo_avicola = self.cleaned_data.get('acceso_modulo_avicola', False)
                perfil.puede_eliminar_registros = self.cleaned_data.get('puede_eliminar_registros', False)
                perfil.save()
            except PerfilUsuario.DoesNotExist:
                # Si no existe, crear uno nuevo
                PerfilUsuario.objects.create(
                    user=user,
                    rol=self.cleaned_data['rol'],
                    telefono=self.cleaned_data.get('telefono', ''),
                    cedula=self.cleaned_data.get('cedula', ''),
                    fecha_nacimiento=self.cleaned_data.get('fecha_nacimiento'),
                    direccion=self.cleaned_data.get('direccion', ''),
                    acceso_modulo_avicola=self.cleaned_data.get('acceso_modulo_avicola', False),
                    puede_eliminar_registros=self.cleaned_data.get('puede_eliminar_registros', False)
                )
        return user


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
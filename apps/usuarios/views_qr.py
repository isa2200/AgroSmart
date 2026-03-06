
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.urls import reverse_lazy, reverse

import qrcode
import io
import base64

from .forms import RegistroVisitanteForm
from .models import PerfilUsuario, RegistroAcceso
from .decorators import admin_usuarios_required

@method_decorator(admin_usuarios_required, name='dispatch')
class GenerarQRVisitanteView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/generar_qr.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # URL de registro de visitantes
        try:
            url_registro = self.request.build_absolute_uri(reverse('usuarios:registro_visitante'))
        except:
            url_registro = "#"
        
        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url_registro)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64 para mostrar en template
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        context['qr_image'] = img_str
        context['url_registro'] = url_registro
        return context

class RegistroVisitanteView(FormView):
    template_name = 'usuarios/registro_visitante.html'
    form_class = RegistroVisitanteForm
    success_url = reverse_lazy('dashboard:principal')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:principal')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        nombre = form.cleaned_data['nombre']
        cedula = form.cleaned_data['cedula']
        
        try:
            # Verificar si ya existe un perfil con esta cédula
            perfil = PerfilUsuario.objects.get(cedula=cedula)
            user = perfil.user
            
            # Actualizar nombre si es necesario
            if not user.first_name:
                user.first_name = nombre.split(' ')[0]
                if len(nombre.split(' ')) > 1:
                    user.last_name = ' '.join(nombre.split(' ')[1:])
                user.save()
                
            messages.info(self.request, f'Bienvenido nuevamente {user.get_full_name()}.')
            
        except PerfilUsuario.DoesNotExist:
            # Crear nuevo usuario visitante
            username = f"visitante_{cedula}"
            user, created = User.objects.get_or_create(username=username)
            
            if created:
                user.set_password(get_random_string(12))
            
            user.first_name = nombre.split(' ')[0]
            if len(nombre.split(' ')) > 1:
                user.last_name = ' '.join(nombre.split(' ')[1:])
            user.save()
            
            # Crear perfil de solo lectura
            PerfilUsuario.objects.create(
                user=user,
                rol='solo_vista',
                cedula=cedula,
                telefono=''
            )
            messages.success(self.request, f'Bienvenido {nombre}. Tu acceso es de solo lectura.')

        # Loguear al usuario
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Registrar acceso
        try:
            RegistroAcceso.objects.create(
                usuario=user,
                ip_address=self.get_client_ip(self.request),
                user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                accion='Login QR Visitante',
                modulo='Usuarios'
            )
        except:
            pass
        
        return super().form_valid(form)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

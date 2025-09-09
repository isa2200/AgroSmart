"""
Vistas para la gestión de usuarios.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import PerfilUsuario, RegistroAcceso
from .forms import RegistroUsuarioForm, PerfilUsuarioForm, LoginForm
from .decorators import role_required


class LoginView(CreateView):
    """
    Vista personalizada de login.
    """
    template_name = 'usuarios/login.html'
    form_class = LoginForm
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:principal')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                # Registrar acceso
                RegistroAcceso.objects.create(
                    usuario=user,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    accion='Login',
                    modulo='Usuarios'
                )
                messages.success(request, f'Bienvenido {user.get_full_name()}')
                return redirect('dashboard:principal')
        return render(request, self.template_name, {'form': form})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(role_required(['superusuario']), name='dispatch')
class UsuarioListView(LoginRequiredMixin, ListView):
    """
    Lista de usuarios del sistema.
    """
    model = User
    template_name = 'usuarios/lista_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.select_related('perfilusuario').filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset.order_by('-date_joined')


@method_decorator(role_required(['superusuario']), name='dispatch')
class CrearUsuarioView(LoginRequiredMixin, CreateView):
    """
    Vista para crear nuevos usuarios.
    """
    model = User
    form_class = RegistroUsuarioForm
    template_name = 'usuarios/crear_usuario.html'
    success_url = reverse_lazy('usuarios:lista')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuario creado exitosamente')
        return response


class PerfilView(LoginRequiredMixin, DetailView):
    """
    Vista del perfil del usuario.
    """
    model = PerfilUsuario
    template_name = 'usuarios/perfil.html'
    context_object_name = 'perfil'
    
    def get_object(self):
        return get_object_or_404(PerfilUsuario, user=self.request.user)


class EditarPerfilView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar el perfil del usuario.
    """
    model = PerfilUsuario
    form_class = PerfilUsuarioForm
    template_name = 'usuarios/editar_perfil.html'
    success_url = reverse_lazy('usuarios:perfil')
    
    def get_object(self):
        return get_object_or_404(PerfilUsuario, user=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Perfil actualizado exitosamente')
        return response
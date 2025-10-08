"""
Vistas para la gestión de usuarios.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, TemplateView
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import PerfilUsuario, RegistroAcceso
from .forms import RegistroUsuarioForm, PerfilUsuarioForm, LoginForm, RegistroCompletoForm, EditarUsuarioForm
from .decorators import role_required, admin_usuarios_required, punto_blanco_required


class LoginView(CreateView):
    """
    Vista personalizada de login.
    """
    template_name = 'usuarios/login.html'
    form_class = LoginForm
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Redirección basada en el rol del usuario autenticado
            try:
                perfil = request.user.perfilusuario
                if perfil.rol == 'punto_blanco':
                    return redirect('punto_blanco:dashboard')
                elif perfil.rol in ['superusuario', 'admin_aves', 'solo_vista']:
                    return redirect('dashboard:principal')
                elif perfil.rol == 'veterinario':
                    return redirect('aves:dashboard')
                else:
                    return redirect('dashboard:principal')
            except:
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
                
                # Redirección basada en el rol del usuario
                try:
                    perfil = user.perfilusuario
                    if perfil.rol == 'punto_blanco':
                        return redirect('punto_blanco:dashboard')
                    elif perfil.rol in ['superusuario', 'admin_aves', 'solo_vista']:
                        return redirect('dashboard:principal')
                    elif perfil.rol == 'veterinario':
                        return redirect('aves:dashboard')
                    else:
                        # Fallback para roles no definidos
                        return redirect('dashboard:principal')
                except:
                    # Si no tiene perfil, redirigir al dashboard principal
                    return redirect('dashboard:principal')
        return render(request, self.template_name, {'form': form})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RegistroView(CreateView):
    """
    Vista para registro de nuevos usuarios con roles.
    """
    model = User
    form_class = RegistroCompletoForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')
    
    def get(self, request, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('dashboard:principal')
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        
        # Registrar la creación del usuario
        RegistroAcceso.objects.create(
            usuario=user,
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            accion='Registro',
            modulo='Usuarios'
        )
        
        messages.success(
            self.request, 
            f'Usuario {user.get_full_name()} creado exitosamente. '
            f'Rol asignado: {user.perfilusuario.get_rol_display()}'
        )
        
        # Opcionalmente, hacer login automático del usuario
        # login(self.request, user)
        # return redirect('dashboard:principal')
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(admin_usuarios_required, name='dispatch')
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


@method_decorator(admin_usuarios_required, name='dispatch')
class CrearUsuarioView(LoginRequiredMixin, CreateView):
    """
    Vista para crear nuevos usuarios.
    """
    model = User
    form_class = RegistroCompletoForm
    template_name = 'usuarios/crear_usuario.html'
    success_url = reverse_lazy('usuarios:lista')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        
        # Registrar la creación del usuario
        RegistroAcceso.objects.create(
            usuario=user,
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            accion='Creación de Usuario',
            modulo='Usuarios'
        )
        
        messages.success(
            self.request, 
            f'Usuario {user.get_full_name()} creado exitosamente. '
            f'Rol asignado: {user.perfilusuario.get_rol_display()}'
        )
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerfilView(LoginRequiredMixin, DetailView):
    """
    Vista del perfil del usuario.
    """
    model = PerfilUsuario
    template_name = 'usuarios/perfil.html'
    context_object_name = 'perfil'
    
    def get_object(self):
        return get_object_or_404(PerfilUsuario, user=self.request.user)


@method_decorator(admin_usuarios_required, name='dispatch')
class UsuarioDetailView(LoginRequiredMixin, DetailView):
    """
    Vista de detalle de un usuario.
    """
    model = User
    template_name = 'usuarios/detalle_usuario.html'
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.get_object()
        try:
            context['perfil'] = usuario.perfilusuario
        except PerfilUsuario.DoesNotExist:
            context['perfil'] = None
        return context


@method_decorator(admin_usuarios_required, name='dispatch')
class EditarUsuarioView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar un usuario.
    """
    model = User
    form_class = EditarUsuarioForm
    template_name = 'usuarios/editar_usuario.html'
    success_url = reverse_lazy('usuarios:lista')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.get_object()
        try:
            context['perfil'] = usuario.perfilusuario
        except PerfilUsuario.DoesNotExist:
            context['perfil'] = None
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Usuario {form.instance.username} actualizado exitosamente')
        return response


@method_decorator(admin_usuarios_required, name='dispatch')
class EliminarUsuarioView(LoginRequiredMixin, DeleteView):
    """
    Vista para eliminar un usuario.
    """
    model = User
    template_name = 'usuarios/eliminar_usuario.html'
    success_url = reverse_lazy('usuarios:lista')
    context_object_name = 'usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.get_object()
        try:
            context['perfil'] = usuario.perfilusuario
        except PerfilUsuario.DoesNotExist:
            context['perfil'] = None
        return context
    
    def delete(self, request, *args, **kwargs):
        usuario = self.get_object()
        username = usuario.username
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Usuario {username} eliminado exitosamente')
        return response


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


@method_decorator(punto_blanco_required, name='dispatch')
class PuntoBlancoDashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard específico para usuarios de Punto Blanco.
    """
    template_name = 'punto_blanco_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener inventarios de huevos disponibles
        from apps.aves.models import InventarioHuevos
        inventarios = InventarioHuevos.objects.filter(cantidad_actual__gt=0)
        
        context.update({
            'inventarios_huevos': inventarios,
            'total_huevos_disponibles': sum(inv.cantidad_actual for inv in inventarios),
        })
        
        return context


@method_decorator(punto_blanco_required, name='dispatch')
class PuntoBlancoInventarioHuevosView(LoginRequiredMixin, ListView):
    """
    Vista de inventario de huevos para Punto Blanco.
    """
    template_name = 'usuarios/punto_blanco_inventario.html'
    context_object_name = 'inventarios'
    
    def get_queryset(self):
        from apps.aves.models import InventarioHuevos
        return InventarioHuevos.objects.all().order_by('categoria', '-fecha_ultima_actualizacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventarios = self.get_queryset()
        
        # Calcular estadísticas
        total_disponible = sum(inv.cantidad_actual for inv in inventarios)
        total_minimo = sum(inv.cantidad_minima for inv in inventarios)
        inventarios_criticos = sum(1 for inv in inventarios if inv.cantidad_actual <= inv.cantidad_minima)
        
        context.update({
            'total_disponible': total_disponible,
            'total_minimo': total_minimo,
            'inventarios_criticos': inventarios_criticos,
            'categorias': inventarios,
        })
        
        return context
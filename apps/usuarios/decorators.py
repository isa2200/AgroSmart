"""
Decoradores personalizados para control de acceso.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden


def role_required(allowed_roles):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
                return redirect('usuarios:login')
            
            try:
                perfil = request.user.perfilusuario
                if perfil.rol not in allowed_roles:
                    messages.error(request, f'No tiene permisos para realizar esta acción. Roles permitidos: {", ".join(allowed_roles)}')
                    return redirect('aves:dashboard')  # Redirigir al dashboard de aves
            except Exception as e:
                messages.error(request, f'Error al verificar permisos: Perfil de usuario no configurado correctamente.')
                return redirect('aves:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def superusuario_required(view_func):
    """Decorador específico para superusuarios."""
    return role_required(['superusuario'])(view_func)


def admin_usuarios_required(view_func):
    """Decorador para administración de usuarios (solo superusuario)."""
    return role_required(['superusuario'])(view_func)


def veterinario_required(view_func):
    """Decorador específico para veterinarios."""
    return role_required(['superusuario', 'veterinario'])(view_func)


def admin_aves_required(view_func):
    """Decorador específico para administradores de aves."""
    return role_required(['superusuario', 'admin_aves'])(view_func)


def punto_blanco_required(view_func):
    """Decorador específico para punto blanco."""
    return role_required(['superusuario', 'punto_blanco'])(view_func)


def puede_editar_required(view_func):
    """Decorador que verifica si el usuario puede editar."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        try:
            perfil = request.user.perfilusuario
            if not perfil.puede_editar():
                messages.error(request, 'No tiene permisos para editar contenido.')
                return redirect('aves:dashboard')
        except:
            messages.error(request, 'Error al verificar permisos')
            return redirect('aves:dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def puede_eliminar_required(view_func):
    """Decorador que verifica si el usuario puede eliminar."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        try:
            perfil = request.user.perfilusuario
            if not perfil.puede_eliminar():
                messages.error(request, 'No tiene permisos para eliminar registros.')
                return redirect('aves:dashboard')
        except:
            messages.error(request, 'Error al verificar permisos')
            return redirect('aves:dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def acceso_modulo_aves_required(view_func):
    """Decorador que verifica acceso al módulo de aves."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        try:
            perfil = request.user.perfilusuario
            if not perfil.puede_acceder_modulo_aves():
                messages.error(request, 'No tiene acceso al módulo avícola.')
                return redirect('dashboard:principal')  # Redirigir al dashboard principal
        except:
            messages.error(request, 'Error al verificar permisos')
            return redirect('dashboard:principal')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def area_access_required(area):
    """
    Decorador que verifica acceso a un área específica.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            
            try:
                perfil = request.user.perfilusuario
                if perfil.tiene_acceso_area(area):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, f'No tienes acceso al área de {area}')
                    return redirect('aves:dashboard')
            except:
                messages.error(request, 'Error al verificar permisos')
                return redirect('aves:dashboard')
        
        return _wrapped_view
    return decorator
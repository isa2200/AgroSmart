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
                    return redirect('aves:lote_list')  # Redirigir a una página específica en lugar de lanzar excepción
            except Exception as e:
                messages.error(request, f'Error al verificar permisos: Perfil de usuario no configurado correctamente.')
                return redirect('aves:lote_list')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def veterinario_required(view_func):
    """Decorador específico para veterinarios."""
    return role_required(['superusuario', 'veterinario'])(view_func)


def admin_aves_required(view_func):
    """Decorador específico para administradores de aves."""
    return role_required(['superusuario', 'admin_aves'])(view_func)


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
                    # En lugar de redirect, usar una página de error
                    from django.http import HttpResponseForbidden
                    from django.template import loader
                    template = loader.get_template('403.html')
                    return HttpResponseForbidden(template.render({'message': f'No tienes acceso al área de {area}'}, request))
            except:
                messages.error(request, 'Error al verificar permisos')
                from django.http import HttpResponseForbidden
                from django.template import loader
                template = loader.get_template('403.html')
                return HttpResponseForbidden(template.render({'message': 'Error al verificar permisos'}, request))
        
        return _wrapped_view
    return decorator
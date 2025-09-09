"""
Decoradores personalizados para control de acceso.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    """Decorador que verifica si el usuario tiene uno de los roles permitidos."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            
            try:
                perfil = request.user.perfilusuario
                print(f"DEBUG: Usuario {request.user.username}, Rol: {perfil.rol}, Roles permitidos: {allowed_roles}")
                if perfil.rol in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'No tienes permisos para acceder a esta sección')
                    from django.http import HttpResponseForbidden
                    from django.template import loader
                    template = loader.get_template('403.html')
                    return HttpResponseForbidden(template.render({'message': 'No tienes permisos para acceder a esta sección'}, request))
            except Exception as e:
                print(f"DEBUG ERROR: {str(e)}")
                messages.error(request, f'Error al verificar permisos: {str(e)}')
                from django.http import HttpResponseForbidden
                from django.template import loader
                template = loader.get_template('403.html')
                return HttpResponseForbidden(template.render({'message': f'Error al verificar permisos: {str(e)}'}, request))
        
        return _wrapped_view
    return decorator


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
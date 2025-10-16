from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def csrf_test(request):
    """Vista de diagnóstico para CSRF y encabezados HTTP"""
    
    # Obtener información del cliente
    client_ip = request.META.get('REMOTE_ADDR')
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    host_header = request.META.get('HTTP_HOST')
    origin_header = request.META.get('HTTP_ORIGIN')
    referer_header = request.META.get('HTTP_REFERER')
    
    # Generar token CSRF
    csrf_token = get_token(request)
    
    # Información completa de headers
    headers_info = {
        'HTTP_HOST': host_header,
        'HTTP_ORIGIN': origin_header,
        'HTTP_REFERER': referer_header,
        'HTTP_X_FORWARDED_FOR': forwarded_for,
        'HTTP_X_FORWARDED_PROTO': request.META.get('HTTP_X_FORWARDED_PROTO'),
        'REMOTE_ADDR': client_ip,
        'SERVER_NAME': request.META.get('SERVER_NAME'),
        'SERVER_PORT': request.META.get('SERVER_PORT'),
    }
    
    # Información de configuración Django
    from django.conf import settings
    config_info = {
        'ALLOWED_HOSTS': getattr(settings, 'ALLOWED_HOSTS', []),
        'CSRF_TRUSTED_ORIGINS': getattr(settings, 'CSRF_TRUSTED_ORIGINS', []),
        'DEBUG': getattr(settings, 'DEBUG', False),
        'USE_X_FORWARDED_HOST': getattr(settings, 'USE_X_FORWARDED_HOST', False),
        'SECURE_PROXY_SSL_HEADER': getattr(settings, 'SECURE_PROXY_SSL_HEADER', None),
    }
    
    response_data = {
        'method': request.method,
        'csrf_token': csrf_token,
        'client_info': {
            'ip': client_ip,
            'forwarded_for': forwarded_for,
            'host': host_header,
            'origin': origin_header,
            'referer': referer_header,
        },
        'headers': headers_info,
        'django_config': config_info,
        'request_url': request.build_absolute_uri(),
        'is_secure': request.is_secure(),
    }
    
    # Si es POST, verificar si el token CSRF es válido
    if request.method == 'POST':
        csrf_token_from_post = request.POST.get('csrfmiddlewaretoken')
        response_data['csrf_validation'] = {
            'token_received': csrf_token_from_post,
            'token_matches': csrf_token_from_post == csrf_token if csrf_token_from_post else False,
        }
    
    return JsonResponse(response_data, indent=2)
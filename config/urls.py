"""
URL configuration for AgroSmart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import csrf_test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('csrf-test/', csrf_test, name='csrf_test'),
    path('', include('apps.dashboard.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('aves/', include('apps.aves.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('punto-blanco/', include('apps.punto_blanco.urls')),
    path('porcinos/', include('apps.porcinos.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar URLs
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Servir MEDIA aunque DEBUG sea False (útil en Docker local)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

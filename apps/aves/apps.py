"""
Configuración de la aplicación avícola.
"""

from django.apps import AppConfig


class AvesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.aves'
    verbose_name = 'Módulo Avícola'
    
    def ready(self):
        """Importar señales cuando la app esté lista."""
        import apps.aves.signals
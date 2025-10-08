from django.apps import AppConfig


class PuntoBlancoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.punto_blanco'
    verbose_name = 'Punto Blanco'
    
    def ready(self):
        import apps.punto_blanco.signals
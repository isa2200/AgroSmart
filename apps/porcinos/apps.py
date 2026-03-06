from django.apps import AppConfig


class PorcinosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.porcinos'
    verbose_name = 'Módulo Porcinos'

    def ready(self):
        import apps.porcinos.signals
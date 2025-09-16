"""
Señales para el módulo avícola.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import BitacoraDiaria, MovimientoHuevos, RegistroModificacion
from .utils import generar_alertas, actualizar_inventario_huevos


@receiver(post_save, sender=BitacoraDiaria)
def procesar_bitacora_diaria(sender, instance, created, **kwargs):
    """Procesa la bitácora diaria después de guardarla."""
    if created:
        # Generar alertas automáticas
        generar_alertas(instance)
        
        # Actualizar inventario de huevos
        actualizar_inventario_huevos(instance)


@receiver(pre_save)
def registrar_modificaciones(sender, instance, **kwargs):
    """Registra modificaciones para auditoría."""
    # Solo para modelos del módulo avícola
    if not sender._meta.app_label == 'aves':
        return
    
    # Solo si el objeto ya existe (es una modificación)
    if instance.pk:
        try:
            objeto_anterior = sender.objects.get(pk=instance.pk)
            campos_modificados = {}
            valores_anteriores = {}
            valores_nuevos = {}
            
            for field in instance._meta.fields:
                field_name = field.name
                valor_anterior = getattr(objeto_anterior, field_name)
                valor_nuevo = getattr(instance, field_name)
                
                if valor_anterior != valor_nuevo:
                    campos_modificados[field_name] = True
                    valores_anteriores[field_name] = str(valor_anterior)
                    valores_nuevos[field_name] = str(valor_nuevo)
            
            if campos_modificados:
                # Aquí podrías obtener el usuario actual del request
                # Por simplicidad, usamos el primer superusuario
                usuario = User.objects.filter(is_superuser=True).first()
                
                RegistroModificacion.objects.create(
                    usuario=usuario,
                    modelo=sender.__name__,
                    objeto_id=instance.pk,
                    accion='UPDATE',
                    campos_modificados=campos_modificados,
                    valores_anteriores=valores_anteriores,
                    valores_nuevos=valores_nuevos
                )
        except sender.DoesNotExist:
            pass
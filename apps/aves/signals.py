"""
Señales para el módulo avícola.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import BitacoraDiaria, MovimientoHuevos, DetalleMovimientoHuevos, RegistroModificacion
from .utils import generar_alertas, actualizar_inventario_huevos, actualizar_inventario_por_movimiento


@receiver(post_save, sender=BitacoraDiaria)
def procesar_bitacora_diaria(sender, instance, created, **kwargs):
    """Procesa la bitácora diaria después de guardarla."""
    if created:
        # Generar alertas automáticas
        generar_alertas(instance)
        
        # Actualizar inventario de huevos
        actualizar_inventario_huevos(instance)


@receiver(post_save, sender=DetalleMovimientoHuevos)
def procesar_movimiento_huevos(sender, instance, created, **kwargs):
    """Actualiza el inventario cuando se registra un movimiento de huevos."""
    if created:
        # Actualizar inventario restando la cantidad movida
        actualizar_inventario_por_movimiento(instance)


@receiver(post_delete, sender=DetalleMovimientoHuevos)
def revertir_movimiento_huevos(sender, instance, **kwargs):
    """Revierte el inventario cuando se elimina un movimiento de huevos."""
    try:
        from .models import InventarioHuevos
        
        # Obtener el inventario para la categoría
        inventario = InventarioHuevos.objects.get(categoria=instance.categoria_huevo)
        
        # Devolver la cantidad al inventario (sumar lo que se había restado)
        cantidad_unidades = instance.cantidad_unidades
        inventario.cantidad_actual += cantidad_unidades
        inventario.save()
        
    except InventarioHuevos.DoesNotExist:
        # Si no existe el inventario, no hacer nada
        pass
    except Exception as e:
        print(f"Error revirtiendo movimiento: {e}")


from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import RegistroModificacion
import json
from datetime import date, datetime
from decimal import Decimal

class DateTimeEncoder(json.JSONEncoder):
    """Encoder personalizado para manejar fechas y decimales."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

@receiver(pre_save)
def registrar_modificaciones(sender, instance, **kwargs):
    """Registra modificaciones para auditoría."""
    # Solo para modelos del módulo avícola
    if not sender._meta.app_label == 'aves':
        return
    
    # Excluir BitacoraDiaria ya que se maneja manualmente en la vista con justificación
    if sender.__name__ == 'BitacoraDiaria':
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
                    # Convertir valores a string de forma segura
                    if isinstance(valor_anterior, (date, datetime)):
                        valores_anteriores[field_name] = valor_anterior.isoformat()
                    else:
                        valores_anteriores[field_name] = str(valor_anterior) if valor_anterior is not None else None
                    
                    if isinstance(valor_nuevo, (date, datetime)):
                        valores_nuevos[field_name] = valor_nuevo.isoformat()
                    else:
                        valores_nuevos[field_name] = str(valor_nuevo) if valor_nuevo is not None else None
            
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
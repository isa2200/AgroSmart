from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DetallePedido


@receiver(post_save, sender=DetallePedido)
def actualizar_total_pedido_save(sender, instance, **kwargs):
    """Actualizar total del pedido cuando se guarda un detalle"""
    instance.pedido.calcular_total()


@receiver(post_delete, sender=DetallePedido)
def actualizar_total_pedido_delete(sender, instance, **kwargs):
    """Actualizar total del pedido cuando se elimina un detalle"""
    instance.pedido.calcular_total()
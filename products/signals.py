from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductVariation
from orders.models import OrderItem
@receiver(post_save, sender=OrderItem)
def update_stock_on_order(sender, instance, created, **kwargs):
    if created and instance.variation:
        instance.variation.stock -= instance.quantity
        instance.variation.save()

@receiver(post_delete, sender=OrderItem)
def restore_stock_on_order_item_delete(sender, instance, **kwargs):
    if instance.variation:
        instance.variation.stock += instance.quantity
        instance.variation.save()
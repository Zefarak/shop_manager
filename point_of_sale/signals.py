from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .transcations_tools import transcation_movement, update_transcation_movement, upgrade_tranascation_on_delete
from .models import OrderItem
from site_settings.constants import WAREHOUSE_ORDERS_TRANSCATIONS


@receiver(post_save, sender=OrderItem)
def update_product_qty_on_create(sender, instance, created, **kwargs):
    if not WAREHOUSE_ORDERS_TRANSCATIONS:
        if created:
            transcation_movement(instance.title, instance.order.order_type, instance.qty)
        else:
            update_transcation_movement(instance.title, instance.order.order_type, instance.old_qty(), instance.qty)


@receiver(post_delete, sender=OrderItem)
def update_product_qty_on_delete(sender, instance, **kwargs):
    if not WAREHOUSE_ORDERS_TRANSCATIONS:
        upgrade_tranascation_on_delete(instance.title, instance.order.order_type, instance.qty)

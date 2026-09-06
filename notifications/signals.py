"""
Fires the instant something happens: a requisition gets approved, a
procurement's status changes, a delivery is logged, stock drops, or
equipment is marked returned.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .services import (
    notify_procurement_approval,
    notify_procurement_status_change,
    notify_delivery_received,
    notify_low_stock,
    notify_critical_stock,
    notify_equipment_return,
)


def _remember_old_status(sender, instance, **kwargs):
    """Runs just before saving — remembers what the status WAS, so post_save can tell if it changed."""
    if instance.pk:
        try:
            instance._old_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


# ---------- 1. Procurement approval ----------
@receiver(pre_save, sender="procurement.Requisition")
def requisition_pre_save(sender, instance, **kwargs):
    _remember_old_status(sender, instance, **kwargs)


@receiver(post_save, sender="procurement.Requisition")
def requisition_post_save(sender, instance, created, **kwargs):
    old_status = getattr(instance, "_old_status", None)
    if instance.status == "approved" and old_status != "approved":
        notify_procurement_approval(instance)


# ---------- 2. Procurement status change ----------
@receiver(pre_save, sender="procurement.Procurement")
def procurement_pre_save(sender, instance, **kwargs):
    _remember_old_status(sender, instance, **kwargs)


@receiver(post_save, sender="procurement.Procurement")
def procurement_post_save(sender, instance, created, **kwargs):
    if created:
        return
    old_status = getattr(instance, "_old_status", None)
    if old_status != instance.status:
        notify_procurement_status_change(instance, instance.status)


# ---------- 3. Delivery received ----------
@receiver(post_save, sender="it_assets.GoodsReceipt")
def goods_receipt_post_save(sender, instance, created, **kwargs):
    if created:
        notify_delivery_received(instance)


# ---------- 4 & 5. Low / Critical stock ----------
@receiver(post_save, sender="it_assets.StockItem")
def stock_item_post_save(sender, instance, created, **kwargs):
    from django.conf import settings
    critical = getattr(settings, "CRITICAL_STOCK_THRESHOLD", 5)
    low = getattr(settings, "LOW_STOCK_THRESHOLD", 15)

    if instance.quantity_available <= critical:
        notify_critical_stock(instance)
    elif instance.quantity_available <= low:
        notify_low_stock(instance)


# ---------- 10. Equipment return ----------
@receiver(post_save, sender="it_assets.EquipmentReturn")
def equipment_return_post_save(sender, instance, created, **kwargs):
    if created:
        notify_equipment_return(instance.issue)
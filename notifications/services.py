"""
The toolbox for creating notifications. Every trigger has its own small,
clearly-named function. Nothing else in the app creates a Notification
directly — everything goes through here, so duplicate-prevention stays
in one place.
"""

from datetime import date
from django.contrib.auth.models import User

from .models import Notification


def create_notification(*, recipient, title, message, notification_type,
                          priority="medium", related_url=None, dedupe_key=None):
    if recipient is None:
        return None
    if dedupe_key and Notification.objects.filter(recipient=recipient, dedupe_key=dedupe_key).exists():
        return None
    return Notification.objects.create(
        recipient=recipient, title=title, message=message,
        notification_type=notification_type, priority=priority,
        related_url=related_url, dedupe_key=dedupe_key,
    )


def get_fallback_staff():
    """Used when there's no single obvious 'owner' for something (e.g. a contract)."""
    return User.objects.filter(is_staff=True, is_active=True)


# ---------- 1. Procurement approval ----------
def notify_procurement_approval(requisition):
    create_notification(
        recipient=requisition.requested_by,
        title="Your Procurement Request Was Approved",
        message=f"Requisition #{requisition.pk} has been approved.",
        notification_type="procurement",
        priority="medium",
        dedupe_key=f"requisition-approved-{requisition.pk}",
    )


# ---------- 2. Procurement status change ----------
def notify_procurement_status_change(procurement, new_status):
    recipients = [u for u in [
        getattr(procurement.requisition, "requested_by", None) if procurement.requisition else None
    ] if u] or list(get_fallback_staff())

    for user in recipients:
        create_notification(
            recipient=user,
            title="Procurement Status Updated",
            message=f"Procurement #{procurement.pk} status changed to '{procurement.get_status_display()}'.",
            notification_type="procurement",
            priority="medium",
            dedupe_key=f"procurement-status-{procurement.pk}-{new_status}",
        )


# ---------- 3. Delivery received ----------
def notify_delivery_received(goods_receipt):
    recipients = [goods_receipt.received_by] if goods_receipt.received_by else list(get_fallback_staff())
    for user in recipients:
        create_notification(
            recipient=user,
            title="Delivery Received",
            message=f"Goods receipt #{goods_receipt.pk} has been logged at '{goods_receipt.store}'.",
            notification_type="procurement",
            priority="medium",
            dedupe_key=f"delivery-received-{goods_receipt.pk}",
        )


# ---------- 4 & 5. Low / Critical stock ----------
def notify_low_stock(stock_item):
    for user in get_fallback_staff():
        create_notification(
            recipient=user,
            title="Low Stock Alert",
            message=f"'{stock_item.name}' is low: {stock_item.quantity_available} {stock_item.unit} left.",
            notification_type="stock",
            priority="high",
            dedupe_key=f"stock-low-{stock_item.pk}-{date.today()}",
        )


def notify_critical_stock(stock_item):
    for user in get_fallback_staff():
        create_notification(
            recipient=user,
            title="Critical Stock Alert",
            message=f"'{stock_item.name}' is critically low: {stock_item.quantity_available} {stock_item.unit} left.",
            notification_type="stock",
            priority="critical",
            dedupe_key=f"stock-critical-{stock_item.pk}-{date.today()}",
        )


# ---------- 6. Warranty expiry ----------
def notify_warranty_expiry(asset, days_left):
    priority = "critical" if days_left <= 7 else "high" if days_left <= 30 else "medium"
    recipients = [asset.assigned_to] if asset.assigned_to else list(get_fallback_staff())
    for user in recipients:
        create_notification(
            recipient=user,
            title="Warranty Expiring Soon",
            message=f"Warranty for '{asset.asset_id}' expires in {days_left} day(s).",
            notification_type="warranty",
            priority=priority,
            dedupe_key=f"warranty-expiry-{asset.pk}-{date.today()}",
        )


# ---------- 7. Contract expiry ----------
def notify_contract_expiry(contract, days_left):
    priority = "critical" if days_left <= 7 else "high" if days_left <= 30 else "medium"
    for user in get_fallback_staff():
        create_notification(
            recipient=user,
            title="Contract Expiring Soon",
            message=f"Contract '{contract.title}' expires in {days_left} day(s).",
            notification_type="contract",
            priority=priority,
            dedupe_key=f"contract-expiry-{contract.pk}-{date.today()}",
        )


# ---------- 8. Pending repair ----------
def notify_pending_repair(asset):
    recipients = [asset.assigned_to] if asset.assigned_to else list(get_fallback_staff())
    for user in recipients:
        create_notification(
            recipient=user,
            title="Asset Still In Repair",
            message=f"'{asset.asset_id}' is still marked as in repair.",
            notification_type="repair",
            priority="high",
            dedupe_key=f"repair-pending-{asset.pk}-{date.today()}",
        )


# ---------- 9. SLA breach ----------
def notify_sla_breach(vendor_issue):
    recipients = [vendor_issue.reported_by] if vendor_issue.reported_by else list(get_fallback_staff())
    for user in recipients:
        create_notification(
            recipient=user,
            title="SLA Breach",
            message=f"Vendor issue '{vendor_issue.title}' ({vendor_issue.vendor.name}) has breached its SLA.",
            notification_type="sla",
            priority="critical",
            dedupe_key=f"sla-breach-{vendor_issue.pk}",
        )


# ---------- 10. Equipment return ----------
def notify_equipment_return(issue):
    recipients = [issue.issued_by] if issue.issued_by else list(get_fallback_staff())
    for user in recipients:
        create_notification(
            recipient=user,
            title="Equipment Returned",
            message=f"'{issue.asset.asset_id}' was returned by {issue.issued_to}.",
            notification_type="asset",
            priority="medium",
            dedupe_key=f"equipment-return-{issue.pk}",
        )


# ---------- 11. Inventory verification ----------
def notify_inventory_verification(asset):
    recipients = [asset.assigned_to] if asset.assigned_to else list(get_fallback_staff())
    for user in recipients:
        create_notification(
            recipient=user,
            title="Inventory Verification Due",
            message=f"'{asset.asset_id}' hasn't been checked in a while and is due for verification.",
            notification_type="inventory",
            priority="medium",
            dedupe_key=f"inventory-verify-{asset.pk}-{date.today()}",
        )


# ---------- 12. Pending acknowledgement ----------
def notify_pending_acknowledgement(issue):
    if not issue.issued_to:
        return
    create_notification(
        recipient=issue.issued_to,
        title="Please Acknowledge Your Assigned Equipment",
        message=f"You still need to confirm receipt of '{issue.asset.asset_id}'.",
        notification_type="acknowledgement",
        priority="high",
        dedupe_key=f"ack-pending-{issue.pk}-{date.today()}",
    )
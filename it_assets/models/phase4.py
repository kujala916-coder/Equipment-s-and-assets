"""
PHASE 4 — Stock Levels (fields already added to StockItem in models_phase1.py),
Physical Verification, Asset Tagging.
Depends on: Asset, StockItem (from models_phase1.py)
"""

from django.conf import settings
from django.db import models

from .phase1 import Asset, StockItem


# ---------------------------------------------------------------------------
# 4.2  Inventory Verification (a physical count session)
# ---------------------------------------------------------------------------
class InventoryVerification(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"

    verification_date = models.DateField(auto_now_add=True)
    conducted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.IN_PROGRESS)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-verification_date"]

    def __str__(self):
        return f"Verification {self.id} ({self.get_status_display()})"


# ---------------------------------------------------------------------------
# 4.3  Inventory Verification Item (line item — one per asset / stock item checked)
# ---------------------------------------------------------------------------
class InventoryVerificationItem(models.Model):
    class FoundStatus(models.TextChoices):
        FOUND = "FOUND", "Found"
        NOT_FOUND = "NOT_FOUND", "Not found"
        DAMAGED = "DAMAGED", "Damaged"
        RELOCATED = "RELOCATED", "Relocated"
        MISTAGGED = "MISTAGGED", "Mistagged"

    verification = models.ForeignKey(InventoryVerification, on_delete=models.CASCADE, related_name="items")
    asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.SET_NULL)
    stock_item = models.ForeignKey(StockItem, null=True, blank=True, on_delete=models.SET_NULL)

    expected_quantity = models.PositiveIntegerField(null=True, blank=True)
    physical_quantity = models.PositiveIntegerField(null=True, blank=True)
    found_status = models.CharField(max_length=15, choices=FoundStatus.choices)
    remarks = models.TextField(blank=True)

    def __str__(self):
        target = self.asset.asset_id if self.asset else self.stock_item.name
        return f"{target}: {self.get_found_status_display()}"


# ---------------------------------------------------------------------------
# 4.4  Inventory Reconciliation (system vs physical count differences)
# ---------------------------------------------------------------------------
class InventoryReconciliation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        INVESTIGATING = "INVESTIGATING", "Investigating"
        ADJUSTED = "ADJUSTED", "Adjusted"

    verification = models.ForeignKey(InventoryVerification, on_delete=models.CASCADE, related_name="reconciliations")
    stock_item = models.ForeignKey(StockItem, null=True, blank=True, on_delete=models.SET_NULL)
    system_quantity = models.PositiveIntegerField()
    physical_quantity = models.PositiveIntegerField()
    difference = models.IntegerField(editable=False)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    adjustment_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    remarks = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.difference = self.physical_quantity - self.system_quantity
        super().save(*args, **kwargs)
        if self.status == self.Status.ADJUSTED and self.stock_item:
            self.stock_item.quantity_available = self.physical_quantity
            self.stock_item.save(update_fields=["quantity_available"])

    def __str__(self):
        return f"Reconciliation: {self.stock_item} (diff {self.difference})"


# ---------------------------------------------------------------------------
# 4.5  Asset Tag (QR code)
# ---------------------------------------------------------------------------
class AssetTag(models.Model):
    """
    Optional model — only needed if you generate/store printable QR labels.
    For an MVP, a view that generates a QR on-the-fly from asset.asset_id
    (using the `qrcode` package) is enough and this model can be skipped.
    """
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name="tag")
    qr_code_image = models.ImageField(upload_to="asset_tags/", blank=True)
    generated_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Tag for {self.asset.asset_id}"

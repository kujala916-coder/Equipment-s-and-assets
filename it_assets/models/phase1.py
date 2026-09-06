"""
PHASE 1 — Asset & Store Foundation
Asset Categories, Registration, Store Inventory, Goods Receipt, Issue/Return/Transfer
"""

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


# ---------------------------------------------------------------------------
# 1.1  Asset Category
# ---------------------------------------------------------------------------
class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="children"
    )
    code_prefix = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Asset categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# 1.2  Vendor lives in the `vendors` app (shared with Procurement/Contracts).
# See vendors.models.Vendor — referenced below by string reference.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1.3  Asset  (serialized, individually tracked items)
# ---------------------------------------------------------------------------
class Asset(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        PROCURED = "PROCURED", "Procured"
        RECEIVED = "RECEIVED", "Received"
        IN_STOCK = "IN_STOCK", "In stock"
        ASSIGNED = "ASSIGNED", "Assigned"
        IN_USE = "IN_USE", "In use"
        UNDER_REPAIR = "UNDER_REPAIR", "Under repair"
        RETURNED = "RETURNED", "Returned"
        REASSIGNED = "REASSIGNED", "Reassigned"
        RETIRED = "RETIRED", "Retired"
        DISPOSED = "DISPOSED", "Disposed"

    asset_id = models.CharField(max_length=30, unique=True, editable=False)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name="assets")
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey('vendors.Vendor', null=True, blank=True, on_delete=models.SET_NULL)

    purchase_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    warranty_start = models.DateField(null=True, blank=True)
    warranty_end = models.DateField(null=True, blank=True)

    location = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_STOCK)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assigned_assets"
    )
    current_department = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.asset_id} — {self.brand} {self.model}".strip()

    def save(self, *args, **kwargs):
        # Auto-generate asset_id like IT-LAP-000125 on first save
        if not self.asset_id:
            prefix = self.category.code_prefix
            last = (
                Asset.objects.filter(category=self.category)
                .order_by("-id")
                .first()
            )
            next_seq = (last.id + 1) if last else 1
            self.asset_id = f"IT-{prefix}-{next_seq:06d}"
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# 1.4  StockItem  (consumables tracked by quantity, not serial number)
# ---------------------------------------------------------------------------
class StockItem(models.Model):
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name="stock_items")
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=20, default="pcs")

    quantity_available = models.PositiveIntegerField(default=0)
    quantity_issued = models.PositiveIntegerField(default=0)
    quantity_damaged = models.PositiveIntegerField(default=0)

    # Phase 4 fields (reorder rules) — included here since they live on the same model
    minimum_stock = models.PositiveIntegerField(default=0)
    maximum_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=0)
    reorder_quantity = models.PositiveIntegerField(default=0)
    is_critical = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.quantity_available} {self.unit})"

    @property
    def needs_reorder(self):
        return self.quantity_available <= self.reorder_level


# ---------------------------------------------------------------------------
# 1.5 / 1.6  Goods Receipt (+ line items)
# ---------------------------------------------------------------------------
class GoodsReceipt(models.Model):
    grn_number = models.CharField(max_length=30, unique=True, editable=False)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.PROTECT, related_name="goods_receipts")
    po_reference = models.CharField(max_length=50, blank=True)
    delivery_date = models.DateField()
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    inspection_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.grn_number

    def save(self, *args, **kwargs):
        if not self.grn_number:
            last = GoodsReceipt.objects.order_by("-id").first()
            next_seq = (last.id + 1) if last else 1
            self.grn_number = f"GRN-{next_seq:06d}"
        super().save(*args, **kwargs)


class GoodsReceiptItem(models.Model):
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    description = models.CharField(max_length=200)

    quantity_received = models.PositiveIntegerField()
    quantity_accepted = models.PositiveIntegerField()
    quantity_rejected = models.PositiveIntegerField(default=0)

    serial_numbers = models.TextField(
        blank=True, help_text="Comma-separated serials, required if is_serialized=True"
    )
    is_serialized = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.description} x{self.quantity_accepted} ({self.receipt.grn_number})"

    def clean(self):
        if self.is_serialized:
            serials = [s.strip() for s in self.serial_numbers.split(",") if s.strip()]
            if len(serials) != self.quantity_accepted:
                raise ValidationError(
                    "Number of serial numbers must match quantity_accepted for serialized items."
                )

    def create_downstream_records(self, vendor, received_date):
        """
        Call this after save() to create Asset rows (serialized)
        or bump StockItem quantity (non-serialized).
        """
        if self.is_serialized:
            serials = [s.strip() for s in self.serial_numbers.split(",") if s.strip()]
            for serial in serials:
                Asset.objects.create(
                    category=self.category,
                    serial_number=serial,
                    vendor=vendor,
                    purchase_date=received_date,
                    status=Asset.Status.IN_STOCK,
                )
        else:
            stock_item, _ = StockItem.objects.get_or_create(
                category=self.category, name=self.description
            )
            stock_item.quantity_available += self.quantity_accepted
            stock_item.save(update_fields=["quantity_available"])


# ---------------------------------------------------------------------------
# 1.7  Stock Transaction (audit log for consumable movement)
# ---------------------------------------------------------------------------
class StockTransaction(models.Model):
    class TransactionType(models.TextChoices):
        RECEIPT = "RECEIPT", "Receipt"
        ISSUE = "ISSUE", "Issue"
        RETURN = "RETURN", "Return"
        TRANSFER = "TRANSFER", "Transfer"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"
        DISPOSAL = "DISPOSAL", "Disposal"

    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.IntegerField(help_text="Positive for stock in, negative for stock out")
    reference = models.CharField(max_length=100, blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} — {self.stock_item.name}"


# ---------------------------------------------------------------------------
# 1.8 / 1.9 / 1.10  Issue, Return, Transfer
# ---------------------------------------------------------------------------
class EquipmentIssue(models.Model):
    asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.SET_NULL, related_name="issues")
    stock_item = models.ForeignKey(StockItem, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)

    issued_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="equipment_received")
    department = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(auto_now_add=True)
    condition = models.CharField(max_length=50, default="Good")
    accessories = models.TextField(blank=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_date = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")

    class Meta:
        ordering = ["-issue_date"]

    def clean(self):
        if bool(self.asset) == bool(self.stock_item):
            raise ValidationError("Exactly one of asset or stock_item must be set.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.asset:
            self.asset.status = Asset.Status.ASSIGNED
            self.asset.assigned_to = self.issued_to
            self.asset.current_department = self.department
            self.asset.save(update_fields=["status", "assigned_to", "current_department"])

    def __str__(self):
        item = self.asset.asset_id if self.asset else self.stock_item.name
        return f"Issue: {item} -> {self.issued_to}"


class EquipmentReturn(models.Model):
    issue = models.OneToOneField(EquipmentIssue, on_delete=models.CASCADE, related_name="return_record")
    return_date = models.DateField(auto_now_add=True)
    condition = models.CharField(max_length=50)
    missing_accessories = models.TextField(blank=True)
    damage_notes = models.TextField(blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Return of {self.issue}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        asset = self.issue.asset
        if asset:
            asset.status = Asset.Status.UNDER_REPAIR if self.damage_notes else Asset.Status.IN_STOCK
            asset.assigned_to = None
            asset.save(update_fields=["status", "assigned_to"])


class AssetTransfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="transfers")
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="transfers_out")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="transfers_in")
    from_department = models.CharField(max_length=100, blank=True)
    to_department = models.CharField(max_length=100, blank=True)
    from_location = models.CharField(max_length=150, blank=True)
    to_location = models.CharField(max_length=150, blank=True)
    transfer_date = models.DateField(auto_now_add=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-transfer_date"]

    def __str__(self):
        return f"Transfer of {self.asset.asset_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.asset.assigned_to = self.to_user
        if self.to_department:
            self.asset.current_department = self.to_department
        if self.to_location:
            self.asset.location = self.to_location
        self.asset.save(update_fields=["assigned_to", "current_department", "location"])

from django import forms

from .models import (
    Asset, AssetCategory, Vendor, StockItem,
    GoodsReceipt, GoodsReceiptItem,
    EquipmentIssue, EquipmentReturn, AssetTransfer,
    FaultReport, RepairRecord,
    InventoryVerification, InventoryVerificationItem, InventoryReconciliation,
)


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "category", "brand", "model", "serial_number", "vendor",
            "purchase_date", "cost", "warranty_start", "warranty_end",
            "location", "status", "current_department", "remarks",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "warranty_start": forms.DateInput(attrs={"type": "date"}),
            "warranty_end": forms.DateInput(attrs={"type": "date"}),
        }


class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ["name", "parent", "code_prefix", "description", "is_active"]


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ["name", "contact_person", "phone", "email", "is_active"]


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = [
            "category", "name", "unit",
            "minimum_stock", "maximum_stock", "reorder_level",
            "reorder_quantity", "is_critical",
        ]


class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = ["vendor", "po_reference", "delivery_date", "inspection_remarks"]
        widgets = {"delivery_date": forms.DateInput(attrs={"type": "date"})}


class GoodsReceiptItemForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptItem
        fields = [
            "category", "description", "quantity_received",
            "quantity_accepted", "quantity_rejected",
            "serial_numbers", "is_serialized",
        ]
        widgets = {
            "serial_numbers": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "SN001, SN002, SN003 (only if serialized)",
            }),
        }


class EquipmentIssueForm(forms.ModelForm):
    class Meta:
        model = EquipmentIssue
        fields = [
            "asset", "stock_item", "quantity", "issued_to",
            "department", "condition", "accessories",
        ]

    def clean(self):
        cleaned = super().clean()
        asset = cleaned.get("asset")
        stock_item = cleaned.get("stock_item")
        if bool(asset) == bool(stock_item):
            raise forms.ValidationError("Select either an asset OR a stock item, not both / neither.")
        return cleaned


class EquipmentReturnForm(forms.ModelForm):
    class Meta:
        model = EquipmentReturn
        fields = ["condition", "missing_accessories", "damage_notes", "remarks"]


class AssetTransferForm(forms.ModelForm):
    class Meta:
        model = AssetTransfer
        fields = [
            "asset", "to_user", "to_department", "to_location", "remarks",
        ]


class FaultReportForm(forms.ModelForm):
    class Meta:
        model = FaultReport
        fields = ["asset", "problem_description", "priority"]
        widgets = {
            "problem_description": forms.Textarea(attrs={"rows": 3}),
        }


class RepairRecordForm(forms.ModelForm):
    class Meta:
        model = RepairRecord
        fields = [
            "technician_assigned", "diagnosis", "warranty_checked",
            "under_warranty", "service_center_vendor", "repair_action",
            "repair_cost", "test_result", "status", "closed_date", "remarks",
        ]
        widgets = {
            "diagnosis": forms.Textarea(attrs={"rows": 2}),
            "repair_action": forms.Textarea(attrs={"rows": 2}),
            "closed_date": forms.DateInput(attrs={"type": "date"}),
        }


class InventoryVerificationForm(forms.ModelForm):
    class Meta:
        model = InventoryVerification
        fields = ["remarks"]


class InventoryVerificationItemForm(forms.ModelForm):
    class Meta:
        model = InventoryVerificationItem
        fields = ["asset", "stock_item", "expected_quantity", "physical_quantity", "found_status", "remarks"]

    def clean(self):
        cleaned = super().clean()
        asset = cleaned.get("asset")
        stock_item = cleaned.get("stock_item")
        if bool(asset) == bool(stock_item):
            raise forms.ValidationError("Select either an asset OR a stock item, not both / neither.")
        return cleaned


class InventoryReconciliationForm(forms.ModelForm):
    class Meta:
        model = InventoryReconciliation
        fields = ["stock_item", "system_quantity", "physical_quantity", "status", "remarks"]

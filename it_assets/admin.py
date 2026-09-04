from django.contrib import admin

from .models import (
    AssetCategory, Vendor, Asset, StockItem,
    GoodsReceipt, GoodsReceiptItem, StockTransaction,
    EquipmentIssue, EquipmentReturn, AssetTransfer,
    FaultReport, RepairRecord, Warranty, WarrantyClaim,
    InventoryVerification, InventoryVerificationItem,
    InventoryReconciliation, AssetTag,
)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("asset_id", "category", "brand", "model", "status", "assigned_to")
    list_filter = ("status", "category")
    search_fields = ("asset_id", "serial_number", "brand", "model")


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity_available", "reorder_level", "is_critical")
    list_filter = ("category", "is_critical")


@admin.register(FaultReport)
class FaultReportAdmin(admin.ModelAdmin):
    list_display = ("asset", "priority", "status", "reported_date")
    list_filter = ("priority", "status")


@admin.register(RepairRecord)
class RepairRecordAdmin(admin.ModelAdmin):
    list_display = ("fault_report", "status", "technician_assigned", "repair_cost")
    list_filter = ("status",)


@admin.register(InventoryVerification)
class InventoryVerificationAdmin(admin.ModelAdmin):
    list_display = ("id", "verification_date", "conducted_by", "status")


# Simple registration for the rest — list/detail views can be customised later
admin.site.register(AssetCategory)
admin.site.register(Vendor)
admin.site.register(GoodsReceipt)
admin.site.register(GoodsReceiptItem)
admin.site.register(StockTransaction)
admin.site.register(EquipmentIssue)
admin.site.register(EquipmentReturn)
admin.site.register(AssetTransfer)
admin.site.register(Warranty)
admin.site.register(WarrantyClaim)
admin.site.register(InventoryVerificationItem)
admin.site.register(InventoryReconciliation)
admin.site.register(AssetTag)

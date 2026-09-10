"""
Models package for the IT Equipment & Stores app.
Split into phase1 / phase3 / phase4 files for readability during development —
Django doesn't care about this, it just needs every model importable from
`app_name.models`, which this file provides.
"""

from .phase1 import (
    Employee,
    AssetCategory,
    Asset,
    StockItem,
    GoodsReceipt,
    GoodsReceiptItem,
    StockTransaction,
    EquipmentIssue,
    EquipmentReturn,
    AssetTransfer,
)

from .phase3 import (
    FaultReport,
    RepairRecord,
    Warranty,
    WarrantyClaim,
)

from .phase4 import (
    InventoryVerification,
    InventoryVerificationItem,
    InventoryReconciliation,
    AssetTag,
)

__all__ = [
    "Employee", "AssetCategory", "Asset", "StockItem",
    "GoodsReceipt", "GoodsReceiptItem", "StockTransaction",
    "EquipmentIssue", "EquipmentReturn", "AssetTransfer",
    "FaultReport", "RepairRecord", "Warranty", "WarrantyClaim",
    "InventoryVerification", "InventoryVerificationItem",
    "InventoryReconciliation", "AssetTag",
]

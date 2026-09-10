from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .models import (
    Employee, Asset, AssetCategory, StockItem,
    GoodsReceipt, GoodsReceiptItem,
    EquipmentIssue, EquipmentReturn, AssetTransfer,
    FaultReport, RepairRecord,
    InventoryVerification, InventoryVerificationItem, InventoryReconciliation,
)
from .forms import (
    EmployeeForm, AssetForm, AssetCategoryForm, StockItemForm,
    GoodsReceiptForm, GoodsReceiptItemForm,
    EquipmentIssueForm, EquipmentReturnForm, AssetTransferForm,
    FaultReportForm, RepairRecordForm,
    InventoryVerificationForm, InventoryVerificationItemForm, InventoryReconciliationForm,
)


# ---------------------------------------------------------------------------
# Dashboard — combined view across all merged apps
# ---------------------------------------------------------------------------
@login_required
def dashboard(request):
    context = {
        # --- Asset & Store (Phase 1) ---
        "total_assets": Asset.objects.count(),
        "assets_in_stock": Asset.objects.filter(status=Asset.Status.IN_STOCK).count(),
        "assets_assigned": Asset.objects.filter(status=Asset.Status.ASSIGNED).count(),
        "assets_under_repair": Asset.objects.filter(status=Asset.Status.UNDER_REPAIR).count(),
        "low_stock_items": StockItem.objects.filter(quantity_available__lte=F("reorder_level")),
        # --- Fault / Repair (Phase 3) ---
        "open_faults": FaultReport.objects.exclude(status=FaultReport.Status.CLOSED).count(),
    }

    # --- Vendors (teammate's app) ---
    try:
        from vendors.models import Vendor, VendorIssue
        context["total_vendors"] = Vendor.objects.count()
        context["active_vendors"] = Vendor.objects.filter(status="active").count()
        context["open_vendor_issues"] = VendorIssue.objects.filter(status__in=["open", "in_progress"]).count()
    except Exception:
        pass

    # --- Procurement (teammate's app) ---
    try:
        from procurement.models import Requisition, Procurement
        context["pending_requisitions"] = Requisition.objects.filter(status="pending").count()
        context["procurements_in_progress"] = Procurement.objects.exclude(
            status__in=["closed", "cancelled"]
        ).count()
    except Exception:
        pass

    # --- Contracts (teammate's app) ---
    try:
        from contracts.models import Contract
        soon = timezone.now().date() + timedelta(days=30)
        context["active_contracts"] = Contract.objects.filter(status="active").count()
        context["contracts_expiring_soon"] = Contract.objects.filter(
            status="active", end_date__lte=soon, end_date__gte=timezone.now().date()
        ).count()
    except Exception:
        pass

    # --- Notifications (teammate's app) ---
    try:
        from notifications.models import Notification
        context["recent_notifications"] = Notification.objects.filter(
            recipient=request.user
        ).order_by("-created_at")[:5]
    except Exception:
        pass

    # --- Audit Log (teammate's app) ---
    try:
        from audit.models import AuditLog
        context["recent_audit_logs"] = AuditLog.objects.order_by("-timestamp")[:5]
    except Exception:
        pass

    return render(request, "it_assets/dashboard.html", context)


# ---------------------------------------------------------------------------
# Employee (asset custody tracking)
# ---------------------------------------------------------------------------
@login_required
@permission_required("it_assets.view_employee", raise_exception=True)
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "it_assets/employee_list.html", {"employees": employees})


@login_required
@permission_required("it_assets.add_employee", raise_exception=True)
def employee_create(request):
    form = EmployeeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        employee = form.save()
        messages.success(request, f"Employee {employee.full_name} added.")
        return redirect("it_assets:employee_list")
    return render(request, "it_assets/employee_form.html", {"form": form})


@login_required
@permission_required("it_assets.view_employee", raise_exception=True)
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, "it_assets/employee_detail.html", {
        "employee": employee,
        "assets_held": employee.assigned_assets.all(),
        "issues": employee.equipment_received.select_related("asset").all(),
        "transfers_in": employee.transfers_in.select_related("asset").all(),
        "transfers_out": employee.transfers_out.select_related("asset").all(),
    })


# ---------------------------------------------------------------------------
# Asset Category
# ---------------------------------------------------------------------------
@login_required
@permission_required("it_assets.view_assetcategory", raise_exception=True)
def category_list(request):
    categories = AssetCategory.objects.all()
    return render(request, "it_assets/category_list.html", {"categories": categories})


@login_required
@permission_required("it_assets.add_assetcategory", raise_exception=True)
def category_create(request):
    form = AssetCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category created.")
        return redirect("it_assets:category_list")
    return render(request, "it_assets/category_form.html", {"form": form})


# ---------------------------------------------------------------------------
# Asset
# ---------------------------------------------------------------------------
@login_required
@permission_required("it_assets.view_asset", raise_exception=True)
def asset_list(request):
    assets = Asset.objects.select_related("category", "assigned_to").all()
    status_filter = request.GET.get("status")
    if status_filter:
        assets = assets.filter(status=status_filter)
    return render(request, "it_assets/asset_list.html", {
        "assets": assets,
        "status_choices": Asset.Status.choices,
        "current_status": status_filter,
    })


@login_required
@permission_required("it_assets.view_asset", raise_exception=True)
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, "it_assets/asset_detail.html", {
        "asset": asset,
        "issues": asset.issues.select_related("issued_to").all(),
        "transfers": asset.transfers.all(),
        "fault_reports": asset.fault_reports.all(),
    })


@login_required
@permission_required("it_assets.add_asset", raise_exception=True)
def asset_create(request):
    form = AssetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        asset = form.save()
        messages.success(request, f"Asset {asset.asset_id} registered.")
        return redirect("it_assets:asset_detail", pk=asset.pk)
    return render(request, "it_assets/asset_form.html", {"form": form})


@login_required
@permission_required("it_assets.change_asset", raise_exception=True)
def asset_update(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    form = AssetForm(request.POST or None, instance=asset)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Asset {asset.asset_id} updated.")
        return redirect("it_assets:asset_detail", pk=asset.pk)
    return render(request, "it_assets/asset_form.html", {"form": form, "asset": asset})


# ---------------------------------------------------------------------------
# Stock Items
# ---------------------------------------------------------------------------
@login_required
@permission_required("it_assets.view_stockitem", raise_exception=True)
def stock_list(request):
    items = StockItem.objects.select_related("category").all()
    return render(request, "it_assets/stock_list.html", {"items": items})


@login_required
@permission_required("it_assets.add_stockitem", raise_exception=True)
def stock_create(request):
    form = StockItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Stock item created.")
        return redirect("it_assets:stock_list")
    return render(request, "it_assets/stock_form.html", {"form": form})


# ---------------------------------------------------------------------------
# Goods Receipt
# ---------------------------------------------------------------------------
@login_required
@permission_required("it_assets.add_goodsreceipt", raise_exception=True)
def goods_receipt_create(request):
    form = GoodsReceiptForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        receipt = form.save(commit=False)
        receipt.received_by = request.user
        receipt.save()
        messages.success(request, f"Goods receipt {receipt.grn_number} created. Now add items.")
        return redirect("it_assets:goods_receipt_add_item", pk=receipt.pk)
    return render(request, "it_assets/goods_receipt_form.html", {"form": form})


@login_required
@permission_required("it_assets.add_goodsreceiptitem", raise_exception=True)
def goods_receipt_add_item(request, pk):
    receipt = get_object_or_404(GoodsReceipt, pk=pk)
    form = GoodsReceiptItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.receipt = receipt
        item.full_clean()
        item.save()
        item.create_downstream_records(vendor=receipt.vendor, received_date=receipt.delivery_date)
        messages.success(request, "Item added and stock/asset records created.")
        return redirect("it_assets:goods_receipt_detail", pk=receipt.pk)
    return render(request, "it_assets/goods_receipt_item_form.html", {"form": form, "receipt": receipt})


@login_required
@permission_required("it_assets.view_goodsreceipt", raise_exception=True)
def goods_receipt_detail(request, pk):
    receipt = get_object_or_404(GoodsReceipt, pk=pk)
    return render(request, "it_assets/goods_receipt_detail.html", {
        "receipt": receipt,
        "items": receipt.items.all(),
    })


# ---------------------------------------------------------------------------
# Equipment Issue / Return / Transfer
# ---------------------------------------------------------------------------
@login_required
@permission_required("it_assets.add_equipmentissue", raise_exception=True)
def issue_create(request):
    form = EquipmentIssueForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        issue = form.save(commit=False)
        issue.issued_by = request.user
        issue.full_clean()
        issue.save()
        messages.success(request, "Equipment issued.")
        return redirect("it_assets:issue_list")
    return render(request, "it_assets/issue_form.html", {"form": form})


@login_required
@permission_required("it_assets.view_equipmentissue", raise_exception=True)
def issue_list(request):
    issues = EquipmentIssue.objects.select_related("asset", "stock_item", "issued_to").all()
    return render(request, "it_assets/issue_list.html", {"issues": issues})


@login_required
@permission_required("it_assets.add_equipmentreturn", raise_exception=True)
def return_create(request, issue_pk):
    issue = get_object_or_404(EquipmentIssue, pk=issue_pk)
    form = EquipmentReturnForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ret = form.save(commit=False)
        ret.issue = issue
        ret.received_by = request.user
        ret.save()
        messages.success(request, "Return recorded.")
        return redirect("it_assets:issue_list")
    return render(request, "it_assets/return_form.html", {"form": form, "issue": issue})


@login_required
@permission_required("it_assets.add_assettransfer", raise_exception=True)
def transfer_create(request):
    form = AssetTransferForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        transfer = form.save(commit=False)
        transfer.from_employee = transfer.asset.assigned_to
        transfer.from_department = transfer.asset.current_department
        transfer.from_location = transfer.asset.location
        transfer.approved_by = request.user
        transfer.save()
        messages.success(request, "Asset transferred.")
        return redirect("it_assets:asset_detail", pk=transfer.asset.pk)
    return render(request, "it_assets/transfer_form.html", {"form": form})


# ---------------------------------------------------------------------------
# PHASE 3 — Fault Reporting & Repair Tracking
# ---------------------------------------------------------------------------
@login_required
@permission_required("it_assets.view_faultreport", raise_exception=True)
def fault_report_list(request):
    faults = FaultReport.objects.select_related("asset", "reported_by").all()
    status_filter = request.GET.get("status")
    if status_filter:
        faults = faults.filter(status=status_filter)
    return render(request, "it_assets/fault_report_list.html", {
        "faults": faults,
        "status_choices": FaultReport.Status.choices,
        "current_status": status_filter,
    })


@login_required
@permission_required("it_assets.add_faultreport", raise_exception=True)
def fault_report_create(request):
    initial = {}
    asset_id = request.GET.get("asset")
    if asset_id:
        initial["asset"] = asset_id
    form = FaultReportForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        fault = form.save(commit=False)
        fault.reported_by = request.user
        fault.save()
        messages.success(request, "Fault reported. Asset marked as under repair.")
        return redirect("it_assets:fault_report_detail", pk=fault.pk)
    return render(request, "it_assets/fault_report_form.html", {"form": form})


@login_required
@permission_required("it_assets.view_faultreport", raise_exception=True)
def fault_report_detail(request, pk):
    fault = get_object_or_404(FaultReport, pk=pk)
    return render(request, "it_assets/fault_report_detail.html", {
        "fault": fault,
        "repairs": fault.repair_records.all(),
    })


@login_required
@permission_required("it_assets.add_repairrecord", raise_exception=True)
def repair_record_create(request, fault_pk):
    fault = get_object_or_404(FaultReport, pk=fault_pk)
    form = RepairRecordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        repair = form.save(commit=False)
        repair.fault_report = fault
        repair.save()
        messages.success(request, "Repair record saved.")
        return redirect("it_assets:fault_report_detail", pk=fault.pk)
    return render(request, "it_assets/repair_record_form.html", {"form": form, "fault": fault})


@login_required
@permission_required("it_assets.change_repairrecord", raise_exception=True)
def repair_record_update(request, pk):
    repair = get_object_or_404(RepairRecord, pk=pk)
    form = RepairRecordForm(request.POST or None, instance=repair)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Repair record updated.")
        return redirect("it_assets:fault_report_detail", pk=repair.fault_report.pk)
    return render(request, "it_assets/repair_record_form.html", {"form": form, "fault": repair.fault_report, "repair": repair})


# ---------------------------------------------------------------------------
# PHASE 4 — Physical Verification & Asset Tagging
# ---------------------------------------------------------------------------
@login_required
@permission_required("it_assets.view_inventoryverification", raise_exception=True)
def verification_list(request):
    verifications = InventoryVerification.objects.select_related("conducted_by").all()
    return render(request, "it_assets/verification_list.html", {"verifications": verifications})


@login_required
@permission_required("it_assets.add_inventoryverification", raise_exception=True)
def verification_create(request):
    form = InventoryVerificationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        verification = form.save(commit=False)
        verification.conducted_by = request.user
        verification.save()
        messages.success(request, "Verification session started.")
        return redirect("it_assets:verification_detail", pk=verification.pk)
    return render(request, "it_assets/verification_form.html", {"form": form})


@login_required
@permission_required("it_assets.view_inventoryverification", raise_exception=True)
def verification_detail(request, pk):
    verification = get_object_or_404(InventoryVerification, pk=pk)
    return render(request, "it_assets/verification_detail.html", {
        "verification": verification,
        "items": verification.items.select_related("asset", "stock_item").all(),
        "reconciliations": verification.reconciliations.select_related("stock_item").all(),
    })


@login_required
@permission_required("it_assets.add_inventoryverificationitem", raise_exception=True)
def verification_add_item(request, pk):
    verification = get_object_or_404(InventoryVerification, pk=pk)
    form = InventoryVerificationItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.verification = verification
        item.full_clean()
        item.save()
        messages.success(request, "Item recorded.")
        return redirect("it_assets:verification_detail", pk=verification.pk)
    return render(request, "it_assets/verification_item_form.html", {"form": form, "verification": verification})


@login_required
@permission_required("it_assets.add_inventoryreconciliation", raise_exception=True)
def verification_add_reconciliation(request, pk):
    verification = get_object_or_404(InventoryVerification, pk=pk)
    form = InventoryReconciliationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        rec = form.save(commit=False)
        rec.verification = verification
        rec.save()
        messages.success(request, "Reconciliation recorded.")
        return redirect("it_assets:verification_detail", pk=verification.pk)
    return render(request, "it_assets/reconciliation_form.html", {"form": form, "verification": verification})


@login_required
@permission_required("it_assets.change_inventoryverification", raise_exception=True)
def verification_complete(request, pk):
    verification = get_object_or_404(InventoryVerification, pk=pk)
    verification.status = InventoryVerification.Status.COMPLETED
    verification.save(update_fields=["status"])
    messages.success(request, "Verification marked as completed.")
    return redirect("it_assets:verification_detail", pk=verification.pk)


@login_required
@permission_required("it_assets.view_asset", raise_exception=True)
def asset_qr_code(request, pk):
    """Generate a QR code image on-the-fly for an asset (encodes the asset detail URL)."""
    from django.http import HttpResponse
    import io

    asset = get_object_or_404(Asset, pk=pk)

    try:
        import qrcode
    except ImportError:
        return HttpResponse(
            "The 'qrcode' package is not installed.\nRun: pip install qrcode[pil]",
            content_type="text/plain", status=501,
        )

    data = request.build_absolute_uri(
        f"/assets/{asset.pk}/"
    )
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")

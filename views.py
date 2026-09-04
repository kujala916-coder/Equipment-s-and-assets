from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Asset, AssetCategory, StockItem,
    GoodsReceipt, GoodsReceiptItem,
    EquipmentIssue, EquipmentReturn, AssetTransfer,
    FaultReport, RepairRecord,
)
from .forms import (
    AssetForm, AssetCategoryForm, VendorForm, StockItemForm,
    GoodsReceiptForm, GoodsReceiptItemForm,
    EquipmentIssueForm, EquipmentReturnForm, AssetTransferForm,
    FaultReportForm, RepairRecordForm,
)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@login_required
def dashboard(request):
    context = {
        "total_assets": Asset.objects.count(),
        "assets_in_stock": Asset.objects.filter(status=Asset.Status.IN_STOCK).count(),
        "assets_assigned": Asset.objects.filter(status=Asset.Status.ASSIGNED).count(),
        "assets_under_repair": Asset.objects.filter(status=Asset.Status.UNDER_REPAIR).count(),
        "low_stock_items": StockItem.objects.filter(quantity_available__lte=F("reorder_level")),
        "open_faults": FaultReport.objects.exclude(status=FaultReport.Status.CLOSED).count(),
    }
    return render(request, "it_assets/dashboard.html", context)


# ---------------------------------------------------------------------------
# Asset Category
# ---------------------------------------------------------------------------
@login_required
def category_list(request):
    categories = AssetCategory.objects.all()
    return render(request, "it_assets/category_list.html", {"categories": categories})


@login_required
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
def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    return render(request, "it_assets/asset_detail.html", {
        "asset": asset,
        "issues": asset.issues.select_related("issued_to").all(),
        "transfers": asset.transfers.all(),
        "fault_reports": asset.fault_reports.all(),
    })


@login_required
def asset_create(request):
    form = AssetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        asset = form.save()
        messages.success(request, f"Asset {asset.asset_id} registered.")
        return redirect("it_assets:asset_detail", pk=asset.pk)
    return render(request, "it_assets/asset_form.html", {"form": form})


@login_required
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
def stock_list(request):
    items = StockItem.objects.select_related("category").all()
    return render(request, "it_assets/stock_list.html", {"items": items})


@login_required
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
def issue_list(request):
    issues = EquipmentIssue.objects.select_related("asset", "stock_item", "issued_to").all()
    return render(request, "it_assets/issue_list.html", {"issues": issues})


@login_required
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
def transfer_create(request):
    form = AssetTransferForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        transfer = form.save(commit=False)
        transfer.from_user = transfer.asset.assigned_to
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
def fault_report_detail(request, pk):
    fault = get_object_or_404(FaultReport, pk=pk)
    return render(request, "it_assets/fault_report_detail.html", {
        "fault": fault,
        "repairs": fault.repair_records.all(),
    })


@login_required
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
def repair_record_update(request, pk):
    repair = get_object_or_404(RepairRecord, pk=pk)
    form = RepairRecordForm(request.POST or None, instance=repair)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Repair record updated.")
        return redirect("it_assets:fault_report_detail", pk=repair.fault_report.pk)
    return render(request, "it_assets/repair_record_form.html", {"form": form, "fault": repair.fault_report, "repair": repair})

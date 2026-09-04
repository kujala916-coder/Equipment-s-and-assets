from django.urls import path
from . import views

app_name = "it_assets"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.category_create, name="category_create"),

    # Assets
    path("assets/", views.asset_list, name="asset_list"),
    path("assets/new/", views.asset_create, name="asset_create"),
    path("assets/<int:pk>/", views.asset_detail, name="asset_detail"),
    path("assets/<int:pk>/edit/", views.asset_update, name="asset_update"),

    # Stock
    path("stock/", views.stock_list, name="stock_list"),
    path("stock/new/", views.stock_create, name="stock_create"),

    # Goods receipt
    path("receipts/new/", views.goods_receipt_create, name="goods_receipt_create"),
    path("receipts/<int:pk>/", views.goods_receipt_detail, name="goods_receipt_detail"),
    path("receipts/<int:pk>/add-item/", views.goods_receipt_add_item, name="goods_receipt_add_item"),

    # Issue / Return / Transfer
    path("issues/", views.issue_list, name="issue_list"),
    path("issues/new/", views.issue_create, name="issue_create"),
    path("issues/<int:issue_pk>/return/", views.return_create, name="return_create"),
    path("transfers/new/", views.transfer_create, name="transfer_create"),

    # Phase 3 — Faults & Repairs
    path("faults/", views.fault_report_list, name="fault_report_list"),
    path("faults/new/", views.fault_report_create, name="fault_report_create"),
    path("faults/<int:pk>/", views.fault_report_detail, name="fault_report_detail"),
    path("faults/<int:fault_pk>/repair/new/", views.repair_record_create, name="repair_record_create"),
    path("repairs/<int:pk>/edit/", views.repair_record_update, name="repair_record_update"),
]

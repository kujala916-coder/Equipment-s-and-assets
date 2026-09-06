"""
Run daily with: python manage.py check_notifications
Covers everything that needs a date/duration check rather than a single
save event: warranty expiry, contract expiry, pending repair, SLA breach,
inventory verification, and pending acknowledgement.
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand

from it_assets.models import Asset, EquipmentIssue
from contracts.models import Contract
from vendors.models import VendorIssue

from notifications.services import (
    notify_warranty_expiry,
    notify_contract_expiry,
    notify_pending_repair,
    notify_sla_breach,
    notify_inventory_verification,
    notify_pending_acknowledgement,
)

# How many days each severity of vendor issue is allowed to stay open
SLA_TARGET_DAYS = {"critical": 1, "high": 3, "medium": 7, "low": 14}

# How often (in days) an asset should be manually re-checked
INVENTORY_CHECK_INTERVAL_DAYS = 180

# How many days is too long to wait for an acknowledgement
ACKNOWLEDGEMENT_GRACE_DAYS = 3


class Command(BaseCommand):
    help = "Checks date/threshold-based conditions and creates notifications."

    def handle(self, *args, **options):
        self.check_warranty()
        self.check_contracts()
        self.check_pending_repairs()
        self.check_sla_breaches()
        self.check_inventory_verification()
        self.check_pending_acknowledgement()
        self.stdout.write(self.style.SUCCESS("Notification check complete."))

    # ---------- 6. Warranty expiry ----------
    def check_warranty(self):
        soon = date.today() + timedelta(days=30)
        assets = Asset.objects.filter(
            warranty_end__isnull=False,
            warranty_end__gte=date.today(),
            warranty_end__lte=soon,
        )
        for asset in assets:
            days_left = (asset.warranty_end - date.today()).days
            notify_warranty_expiry(asset, days_left)

    # ---------- 7. Contract expiry ----------
    def check_contracts(self):
        soon = date.today() + timedelta(days=30)
        contracts = Contract.objects.filter(
            status="active",
            end_date__gte=date.today(),
            end_date__lte=soon,
        )
        for contract in contracts:
            days_left = (contract.end_date - date.today()).days
            notify_contract_expiry(contract, days_left)

    # ---------- 8. Pending repair ----------
    def check_pending_repairs(self):
        for asset in Asset.objects.filter(status=Asset.Status.UNDER_REPAIR):
            notify_pending_repair(asset)

    # ---------- 9. SLA breach ----------
    def check_sla_breaches(self):
        open_issues = VendorIssue.objects.filter(status__in=["open", "in_progress"])
        for issue in open_issues:
            allowed_days = SLA_TARGET_DAYS.get(issue.severity, 7)
            deadline = issue.reported_date.date() + timedelta(days=allowed_days)
            if date.today() > deadline:
                notify_sla_breach(issue)

    # ---------- 11. Inventory verification ----------
    def check_inventory_verification(self):
        cutoff = date.today() - timedelta(days=INVENTORY_CHECK_INTERVAL_DAYS)
        assets = Asset.objects.filter(updated_at__date__lt=cutoff).exclude(status=Asset.Status.RETIRED)
        for asset in assets:
            notify_inventory_verification(asset)

    # ---------- 12. Pending acknowledgement ----------
    def check_pending_acknowledgement(self):
        cutoff = date.today() - timedelta(days=ACKNOWLEDGEMENT_GRACE_DAYS)
        issues = EquipmentIssue.objects.filter(
            acknowledged=False,
            return_record__isnull=True,
            issue_date__lte=cutoff,
        )
        for issue in issues:
            notify_pending_acknowledgement(issue)
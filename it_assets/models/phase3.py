"""
PHASE 3 — Fault Reporting, Repair Tracking, Warranty Management
Depends on: Asset, Vendor (from models_phase1.py)
"""

from django.conf import settings
from django.db import models

from .phase1 import Asset


# ---------------------------------------------------------------------------
# 3.1  Fault Report
# ---------------------------------------------------------------------------
class FaultReport(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        CLOSED = "CLOSED", "Closed"

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="fault_reports")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    problem_description = models.TextField()
    reported_date = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)

    class Meta:
        ordering = ["-reported_date"]

    def __str__(self):
        return f"Fault: {self.asset.asset_id} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self.asset.status = Asset.Status.UNDER_REPAIR
            self.asset.save(update_fields=["status"])


# ---------------------------------------------------------------------------
# 3.2  Repair Record
# ---------------------------------------------------------------------------
class RepairRecord(models.Model):
    class Status(models.TextChoices):
        FAULT_REPORTED = "FAULT_REPORTED", "Fault reported"
        TECHNICIAN_ASSIGNED = "TECHNICIAN_ASSIGNED", "Technician assigned"
        DIAGNOSIS = "DIAGNOSIS", "Diagnosis"
        WARRANTY_CHECK = "WARRANTY_CHECK", "Warranty check"
        VENDOR_SERVICE_CENTER = "VENDOR_SERVICE_CENTER", "At vendor service center"
        REPAIR_IN_PROGRESS = "REPAIR_IN_PROGRESS", "Repair in progress"
        TESTING = "TESTING", "Testing"
        RETURNED_TO_USER = "RETURNED_TO_USER", "Returned to user"
        CLOSED = "CLOSED", "Closed"

    class TestResult(models.TextChoices):
        PASS = "PASS", "Pass"
        FAIL = "FAIL", "Fail"

    fault_report = models.ForeignKey(FaultReport, on_delete=models.CASCADE, related_name="repair_records")
    technician_assigned = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="repairs_handled"
    )
    diagnosis = models.TextField(blank=True)
    warranty_checked = models.BooleanField(default=False)
    under_warranty = models.BooleanField(null=True, blank=True)
    service_center_vendor = models.ForeignKey('vendors.Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    repair_action = models.TextField(blank=True)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    test_result = models.CharField(max_length=10, choices=TestResult.choices, blank=True)
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.FAULT_REPORTED)
    closed_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Repair for {self.fault_report.asset.asset_id} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == self.Status.CLOSED:
            asset = self.fault_report.asset
            asset.status = Asset.Status.IN_USE if asset.assigned_to else Asset.Status.IN_STOCK
            asset.save(update_fields=["status"])
            self.fault_report.status = FaultReport.Status.CLOSED
            self.fault_report.save(update_fields=["status"])


# ---------------------------------------------------------------------------
# 3.3  Warranty  (only needed if an asset has multiple/renewed warranty periods
#                 — for a simple MVP you can skip this and just use
#                 Asset.warranty_start / Asset.warranty_end)
# ---------------------------------------------------------------------------
class Warranty(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="warranties")
    warranty_provider = models.CharField(max_length=150)
    warranty_type = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    terms = models.TextField(blank=True)

    class Meta:
        ordering = ["-end_date"]

    def __str__(self):
        return f"Warranty for {self.asset.asset_id} (till {self.end_date})"

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.end_date < timezone.now().date()


# ---------------------------------------------------------------------------
# 3.4  Warranty Claim
# ---------------------------------------------------------------------------
class WarrantyClaim(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        RESOLVED = "RESOLVED", "Resolved"
        REJECTED = "REJECTED", "Rejected"

    warranty = models.ForeignKey(Warranty, on_delete=models.CASCADE, related_name="claims")
    claim_date = models.DateField(auto_now_add=True)
    issue_description = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SUBMITTED)
    resolution = models.TextField(blank=True)

    class Meta:
        ordering = ["-claim_date"]

    def __str__(self):
        return f"Claim on {self.warranty} — {self.get_status_display()}"

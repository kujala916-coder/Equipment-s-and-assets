from django.db import models
from vendors.models import Vendor


class ProcurementPlan(models.Model):
    PERIOD_CHOICES = [
        ('yearly', 'Yearly'),
        ('quarterly', 'Quarterly'),
    ]

    title = models.CharField(max_length=255)
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    fiscal_year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    approved = models.BooleanField(default=False)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.fiscal_year})"


class ProcurementRequirement(models.Model):
    plan = models.ForeignKey(ProcurementPlan, on_delete=models.CASCADE, related_name='requirements')
    item_name = models.CharField(max_length=255)
    category = models.ForeignKey('it_assets.AssetCategory', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    estimated_unit_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    justification = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.item_name} x{self.quantity}"


class Requisition(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    requirement = models.ForeignKey(ProcurementRequirement, on_delete=models.CASCADE, related_name='requisitions')
    requested_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    requested_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='approved_requisitions', blank=True)
    approval_date = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Requisition #{self.id} - {self.status}"


class Procurement(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('tender_issued', 'Tender Issued'),
        ('evaluation', 'Under Evaluation'),
        ('po_issued', 'PO Issued'),
        ('delivered', 'Delivered'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]

    requisition = models.ForeignKey(Requisition, on_delete=models.SET_NULL, null=True, blank=True, related_name='procurements')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='procurements')
    tender_number = models.CharField(max_length=100, blank=True, null=True)
    po_number = models.CharField(max_length=100, blank=True, null=True)
    tender_date = models.DateField(blank=True, null=True)
    po_date = models.DateField(blank=True, null=True)
    expected_delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Procurement {self.po_number or self.tender_number or self.id}"


class ProcurementItem(models.Model):
    procurement = models.ForeignKey(Procurement, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    category = models.ForeignKey('it_assets.AssetCategory', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} x{self.quantity}"


class TechnicalSpecification(models.Model):
    procurement_item = models.ForeignKey(ProcurementItem, on_delete=models.CASCADE, related_name='specifications')
    spec_name = models.CharField(max_length=255, help_text="e.g. Processor, RAM, Storage")
    required_value = models.CharField(max_length=255, help_text="e.g. i7, 16GB, 512GB SSD")
    mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.spec_name}: {self.required_value}"


class TechnicalEvaluation(models.Model):
    procurement = models.ForeignKey(Procurement, on_delete=models.CASCADE, related_name='evaluations')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='technical_evaluations')
    evaluated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    evaluation_date = models.DateTimeField(auto_now_add=True)
    overall_result = models.CharField(
        max_length=20,
        choices=[('pass', 'Pass'), ('fail', 'Fail'), ('pending', 'Pending')],
        default='pending'
    )
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Evaluation - {self.vendor.name} ({self.procurement})"


class EvaluationItem(models.Model):
    evaluation = models.ForeignKey(TechnicalEvaluation, on_delete=models.CASCADE, related_name='evaluation_items')
    specification = models.ForeignKey(TechnicalSpecification, on_delete=models.CASCADE, related_name='evaluation_items')
    offered_value = models.CharField(max_length=255)
    result = models.CharField(max_length=10, choices=[('pass', 'Pass'), ('fail', 'Fail')])
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.specification.spec_name} - {self.result}"
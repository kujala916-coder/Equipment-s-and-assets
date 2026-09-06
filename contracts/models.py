from django.db import models
from vendors.models import Vendor


class Contract(models.Model):
    CONTRACT_TYPE_CHOICES = [
        ('amc', 'Annual Maintenance Contract'),
        ('license', 'Software License'),
        ('internet', 'Internet Service'),
        ('lease', 'Lease Agreement'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('renewed', 'Renewed'),
    ]

    title = models.CharField(max_length=255)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='contracts')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    contract_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    document = models.FileField(upload_to='contracts/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_contract_type_display()})"


class ContractRenewal(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='renewals')
    previous_end_date = models.DateField()
    new_end_date = models.DateField()
    renewed_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    renewed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    renewal_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Renewal of {self.contract.title} - {self.new_end_date}"


class License(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='licenses')
    software_name = models.CharField(max_length=255)
    license_key = models.CharField(max_length=255, blank=True, null=True)
    seats = models.PositiveIntegerField(default=1, help_text="Number of licensed users/devices")
    assigned_to = models.ForeignKey('it_assets.Asset', on_delete=models.SET_NULL, null=True, blank=True, related_name='licenses')
    expiry_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.software_name} ({self.contract.title})"
from django.db import models


class Vendor(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blacklisted', 'Blacklisted'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class VendorContact(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.vendor.name})"


class VendorPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='performance_records')
    evaluation_date = models.DateField()
    delivery_time_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Score out of 10")
    sla_compliance_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Score out of 10")
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Score out of 10")
    overall_rating = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.evaluation_date}"


class VendorIssue(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='issues')
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    reported_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='reported_vendor_issues')
    reported_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.vendor.name}"


class VendorEscalation(models.Model):
    issue = models.ForeignKey(VendorIssue, on_delete=models.CASCADE, related_name='escalations')
    escalated_to = models.CharField(max_length=255, help_text="Person/department escalated to")
    escalation_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    resolution_notes = models.TextField(blank=True, null=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Escalation for {self.issue.title}"



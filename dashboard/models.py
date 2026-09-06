from django.db import models


class SavedReport(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='saved_reports')
    report_type = models.CharField(max_length=100, help_text="e.g. asset_summary, vendor_performance")
    filters = models.JSONField(blank=True, null=True, help_text="Stored filter parameters as JSON")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
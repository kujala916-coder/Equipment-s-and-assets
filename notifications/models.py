from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("procurement", "Procurement"),
        ("stock", "Stock"),
        ("warranty", "Warranty"),
        ("contract", "Contract"),
        ("repair", "Repair"),
        ("sla", "SLA"),
        ("asset", "Asset"),
        ("inventory", "Inventory"),
        ("acknowledgement", "Acknowledgement"),
        ("general", "General"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default="general")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    related_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Still used internally to stop the automatic checks from creating duplicates.
    # This has nothing to do with read/unread — don't remove it.
    dedupe_key = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]  # newest first, always
        indexes = [
            models.Index(fields=["recipient", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
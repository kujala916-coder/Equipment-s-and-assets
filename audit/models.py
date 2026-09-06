from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """
    One row = one important thing that happened in the system.
    This table is write-once: nothing in this app ever updates or
    deletes a row after it's created (see admin.py).
    """

    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    actor_username = models.CharField(max_length=150, blank=True, null=True)

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)

    app_label = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=255, blank=True, null=True)

    changes = models.JSONField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['app_label', 'model_name', 'object_id']),
            models.Index(fields=['actor', 'timestamp']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        who = self.actor_username or 'System'
        return f"{who} {self.action} {self.model_name} #{self.object_id} @ {self.timestamp:%d-%b-%Y %H:%M}"
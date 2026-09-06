"""
Run this on a schedule (e.g. once a day) with:
    python manage.py delete_old_notifications

Deletes any notification older than 30 days, no matter its type or
priority. There is no read/unread check involved — age is the only
thing that matters now.
"""

from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand

from notifications.models import Notification

RETENTION_DAYS = 30


class Command(BaseCommand):
    help = f"Deletes notifications older than {RETENTION_DAYS} days."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
        deleted_count, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted_count} notification(s) older than {RETENTION_DAYS} days.")
        )
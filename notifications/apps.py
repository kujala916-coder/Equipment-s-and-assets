from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        from . import signals  # noqa: F401 -- registers the signal handlers
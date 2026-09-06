"""
Django signals (post_save/post_delete) fire deep inside the ORM — they
don't get passed the current HTTP request, so they have no way to know
"which user is doing this" on their own.

This middleware fixes that: on every request it stashes the current
user in a thread-local variable. signals.py then reads it from there
when it writes an AuditLog row.
"""

import threading

_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


def get_current_ip():
    return getattr(_thread_locals, 'ip', None)


def _get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class AuditMiddleware:
    """Add 'audit.middleware.AuditMiddleware' to MIDDLEWARE in settings.py."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        _thread_locals.ip = _get_client_ip(request)
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.user = None
            _thread_locals.ip = None
        return response
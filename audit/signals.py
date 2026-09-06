"""
This is the heart of the audit system.

We connect ONE listener to Django's pre_save / post_save / post_delete
signals with no specific "sender" model. That means it fires for EVERY
model save/delete in the whole project, automatically — no matter which
view, form, admin screen, script, or future feature triggers it.
"""

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import AuditLog
from .middleware import get_current_user, get_current_ip

AUDITED_APPS = {'it_assets', 'procurement', 'vendors', 'contracts'}
IGNORED_FIELDS = {'updated_at'}


def _is_audited(sender):
    if not hasattr(sender, '_meta'):
        return False
    if sender is AuditLog:
        return False
    return sender._meta.app_label in AUDITED_APPS


def _serialize_value(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _snapshot(instance):
    data = {}
    for field in instance._meta.fields:
        name = field.name
        if name in IGNORED_FIELDS:
            continue
        try:
            data[name] = _serialize_value(getattr(instance, name))
        except Exception:
            continue
    return data


def _object_repr(instance):
    try:
        return str(instance)[:255]
    except Exception:
        return None


def _write_log(instance, action, changes):
    user = get_current_user()
    actor = user if (user is not None and getattr(user, 'is_authenticated', False)) else None
    AuditLog.objects.create(
        actor=actor,
        actor_username=getattr(actor, 'username', None) if actor else None,
        action=action,
        app_label=instance._meta.app_label,
        model_name=instance._meta.model_name,
        object_id=str(instance.pk),
        object_repr=_object_repr(instance),
        changes=changes,
        ip_address=get_current_ip(),
    )


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if not _is_audited(sender):
        return
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._audit_old_snapshot = _snapshot(old)
        except sender.DoesNotExist:
            instance._audit_old_snapshot = None
    else:
        instance._audit_old_snapshot = None


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if not _is_audited(sender):
        return

    new_snapshot = _snapshot(instance)

    if created:
        _write_log(instance, 'create', new_snapshot)
        return

    old_snapshot = getattr(instance, '_audit_old_snapshot', None) or {}
    diff = {}
    for field_name, new_value in new_snapshot.items():
        old_value = old_snapshot.get(field_name)
        if old_value != new_value:
            diff[field_name] = {'old': old_value, 'new': new_value}

    if diff:
        _write_log(instance, 'update', diff)


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not _is_audited(sender):
        return
    _write_log(instance, 'delete', _snapshot(instance))
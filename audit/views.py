from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from .models import AuditLog


@login_required
@permission_required('audit.view_auditlog', raise_exception=True)
def audit_log_list(request):
    logs = AuditLog.objects.select_related('actor').all()

    action = request.GET.get('action')
    app_label = request.GET.get('app_label')
    q = request.GET.get('q')

    if action:
        logs = logs.filter(action=action)
    if app_label:
        logs = logs.filter(app_label=app_label)
    if q:
        logs = logs.filter(object_repr__icontains=q)

    logs = logs[:500]

    return render(request, 'audit/audit_log_list.html', {
        'logs': logs,
        'action_choices': AuditLog.ACTION_CHOICES,
        'selected_action': action or '',
        'selected_app': app_label or '',
        'query': q or '',
    })
from django.shortcuts import render
from django.http import HttpResponse
from .models import SavedReport
from procurement.models import Procurement
from vendors.models import Vendor, VendorIssue
from contracts.models import Contract
from notifications.models import Notification


def dashboard_home(request):
    context = {
        'total_vendors': Vendor.objects.count(),
        'total_procurements': Procurement.objects.count(),
        'total_contracts': Contract.objects.count(),
        'active_contracts': Contract.objects.filter(status='active').count(),
        'open_vendor_issues': VendorIssue.objects.filter(status='open').count(),
    }

    if request.user.is_authenticated:
        context['recent_notifications'] = Notification.objects.filter(
            recipient=request.user
        )[:5]

    return render(request, 'dashboard/dashboard_home.html', context)


def saved_report_list(request):
    return HttpResponse(f"Total Saved Reports: {SavedReport.objects.count()}")
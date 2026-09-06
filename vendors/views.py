from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import (
    VendorForm, VendorContactForm, VendorPerformanceForm,
    VendorIssueForm, VendorEscalationForm
)


def vendor_list(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor saved.")
            return redirect('vendors:vendor_list')
    else:
        form = VendorForm()

    return render(request, 'vendors/generic_form.html', {
        'form': form, 'form_title': 'Vendor'
    })


def contact_list(request):
    if request.method == 'POST':
        form = VendorContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor contact saved.")
            return redirect('vendors:contact_list')
    else:
        form = VendorContactForm()

    return render(request, 'vendors/generic_form.html', {
        'form': form, 'form_title': 'Vendor Contact'
    })


def performance_list(request):
    if request.method == 'POST':
        form = VendorPerformanceForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            if not record.overall_rating:
                record.overall_rating = (
                    record.delivery_time_score +
                    record.sla_compliance_score +
                    record.quality_score
                ) / 3
            record.save()
            messages.success(request, "Vendor performance record saved.")
            return redirect('vendors:performance_list')
    else:
        form = VendorPerformanceForm()

    return render(request, 'vendors/generic_form.html', {
        'form': form, 'form_title': 'Vendor Performance'
    })


def issue_list(request):
    if request.method == 'POST':
        form = VendorIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            if request.user.is_authenticated:
                issue.reported_by = request.user
            issue.save()
            messages.success(request, "Vendor issue saved.")
            return redirect('vendors:issue_list')
    else:
        form = VendorIssueForm()

    return render(request, 'vendors/generic_form.html', {
        'form': form, 'form_title': 'Vendor Issue'
    })


def escalation_list(request):
    if request.method == 'POST':
        form = VendorEscalationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor escalation saved.")
            return redirect('vendors:escalation_list')
    else:
        form = VendorEscalationForm()

    return render(request, 'vendors/generic_form.html', {
        'form': form, 'form_title': 'Vendor Escalation'
    })
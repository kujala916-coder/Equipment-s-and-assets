from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContractForm, ContractRenewalForm, LicenseForm, SLAForm


def contract_list(request):
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Contract saved.")
            return redirect('contracts:contract_list')
    else:
        form = ContractForm()

    return render(request, 'contracts/generic_form.html', {
        'form': form, 'form_title': 'Contract', 'is_file_form': True
    })


def renewal_list(request):
    if request.method == 'POST':
        form = ContractRenewalForm(request.POST)
        if form.is_valid():
            renewal = form.save(commit=False)
            if request.user.is_authenticated:
                renewal.renewed_by = request.user
            renewal.save()
            messages.success(request, "Contract renewal saved.")
            return redirect('contracts:renewal_list')
    else:
        form = ContractRenewalForm()

    return render(request, 'contracts/generic_form.html', {
        'form': form, 'form_title': 'Contract Renewal'
    })


def license_add(request):
    if request.method == 'POST':
        form = LicenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "License saved.")
            return redirect('contracts:license_add')
    else:
        form = LicenseForm()
    return render(request, 'contracts/generic_form.html', {
        'form': form, 'form_title': 'Add License'
    })


def license_renew(request):
    if request.method == 'POST':
        form = LicenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "License renewed.")
            return redirect('contracts:license_renew')
    else:
        form = LicenseForm()
    return render(request, 'contracts/generic_form.html', {
        'form': form, 'form_title': 'Renew License'
    })


def sla_add(request):
    if request.method == 'POST':
        form = SLAForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "SLA saved.")
            return redirect('contracts:sla_add')
    else:
        form = SLAForm()
    return render(request, 'contracts/generic_form.html', {
        'form': form, 'form_title': 'Add SLA'
    })


def sla_renew(request):
    if request.method == 'POST':
        form = SLAForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "SLA renewed.")
            return redirect('contracts:sla_renew')
    else:
        form = SLAForm()
    return render(request, 'contracts/generic_form.html', {
        'form': form, 'form_title': 'Renew SLA'
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContractForm, ContractRenewalForm, LicenseForm


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


def license_list(request):
    if request.method == 'POST':
        form = LicenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "License saved.")
            return redirect('contracts:license_list')
    else:
        form = LicenseForm()

    return render(request, 'contracts/generic_form.html', {
        'form': form, 'form_title': 'License'
    })
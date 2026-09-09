from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import (
    ProcurementPlanForm, ProcurementRequirementForm, RequisitionForm,
    ProcurementForm, ProcurementItemForm, TechnicalSpecificationForm,
    TechnicalEvaluationForm, EvaluationItemForm
)


def plan_list(request):
    if request.method == 'POST':
        form = ProcurementPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Procurement plan saved.")
            return redirect('procurement:plan_list')
    else:
        form = ProcurementPlanForm()

    return render(request, 'procurement/generic_form.html', {
        'form': form, 'form_title': 'Procurement Plan'
    })


def requirement_list(request):
    if request.method == 'POST':
        form = ProcurementRequirementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Procurement requirement saved.")
            return redirect('procurement:requirement_list')
    else:
        form = ProcurementRequirementForm()

    return render(request, 'procurement/generic_form.html', {
        'form': form, 'form_title': 'Procurement Requirement'
    })


def requisition_list(request):
    if request.method == 'POST':
        form = RequisitionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Requisition saved.")
            return redirect('procurement:requisition_list')
    else:
        form = RequisitionForm()

    return render(request, 'procurement/generic_form.html', {
        'form': form, 'form_title': 'Requisition'
    })


def procurement_list(request):
    if request.method == 'POST':
        form = ProcurementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Procurement record saved.")
            return redirect('procurement:procurement_list')
    else:
        form = ProcurementForm()

    return render(request, 'procurement/generic_form.html', {
        'form': form, 'form_title': 'Procurement'
    })


def procurement_item_list(request):
    if request.method == 'POST':
        form = ProcurementItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Procurement item saved.")
            return redirect('procurement:procurement_item_list')
    else:
        form = ProcurementItemForm()

    return render(request, 'procurement/generic_form.html', {
        'form': form, 'form_title': 'Procurement Item'
    })


def specification_list(request):
    if request.method == 'POST':
        form = TechnicalSpecificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Technical specification saved.")
            return redirect('procurement:specification_list')
    else:
        form = TechnicalSpecificationForm()

    return render(request, 'procurement/generic_form.html', {
        'form': form, 'form_title': 'Technical Specification'
    })


def evaluation_list(request):
    if request.method == 'POST':
        form = TechnicalEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            if request.user.is_authenticated:
                evaluation.evaluated_by = request.user
            evaluation.save()
            messages.success(request, "Technical evaluation saved.")
            return redirect('procurement:evaluation_list')
    else:
        form = TechnicalEvaluationForm()

    return render(request, 'procurement/generic_form.html', {
        'form': form, 'form_title': 'Technical Evaluation'
    })


def evaluation_item_list(request):
    if request.method == 'POST':
        form = EvaluationItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Evaluation item saved.")
            return redirect('procurement:evaluation_item_list')
    else:
        form = EvaluationItemForm()

    return render(request, 'procurement/generic_form.html', {
        'form': form, 'form_title': 'Evaluation Item'
    })
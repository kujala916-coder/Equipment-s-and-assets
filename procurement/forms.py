from django import forms
from .models import (
    ProcurementPlan, ProcurementRequirement, Requisition,
    Procurement, ProcurementItem, TechnicalSpecification,
    TechnicalEvaluation, EvaluationItem
)


class BootstrapModelForm(forms.ModelForm):
    """Adds Bootstrap classes to every widget automatically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class ProcurementPlanForm(BootstrapModelForm):
    class Meta:
        model = ProcurementPlan
        fields = ['title', 'period_type', 'fiscal_year', 'start_date',
                  'end_date', 'total_budget', 'approved']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ProcurementRequirementForm(BootstrapModelForm):
    class Meta:
        model = ProcurementRequirement
        fields = ['plan', 'item_name', 'category', 'quantity',
                  'estimated_unit_cost', 'justification']


class RequisitionForm(BootstrapModelForm):
    class Meta:
        model = Requisition
        fields = ['requirement', 'status', 'approved_by', 'remarks']


class ProcurementForm(BootstrapModelForm):
    class Meta:
        model = Procurement
        fields = ['requisition', 'vendor', 'tender_number', 'po_number',
                  'tender_date', 'po_date', 'expected_delivery_date',
                  'actual_delivery_date', 'total_value', 'status']
        widgets = {
            'tender_date': forms.DateInput(attrs={'type': 'date'}),
            'po_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ProcurementItemForm(BootstrapModelForm):
    class Meta:
        model = ProcurementItem
        fields = ['procurement', 'item_name', 'category', 'quantity', 'unit_price']


class TechnicalSpecificationForm(BootstrapModelForm):
    class Meta:
        model = TechnicalSpecification
        fields = ['procurement_item', 'spec_name', 'required_value', 'mandatory']


class TechnicalEvaluationForm(BootstrapModelForm):
    class Meta:
        model = TechnicalEvaluation
        fields = ['procurement', 'vendor', 'overall_result', 'remarks']


class EvaluationItemForm(BootstrapModelForm):
    class Meta:
        model = EvaluationItem
        fields = ['evaluation', 'specification', 'offered_value', 'result', 'comments']
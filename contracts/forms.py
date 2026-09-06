from django import forms
from .models import Contract, ContractRenewal, License


class BootstrapModelForm(forms.ModelForm):
    """Adds Bootstrap classes to every widget automatically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'


class ContractForm(BootstrapModelForm):
    class Meta:
        model = Contract
        fields = ['title', 'vendor', 'contract_type', 'contract_number',
                  'start_date', 'end_date', 'value', 'status', 'document', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ContractRenewalForm(BootstrapModelForm):
    class Meta:
        model = ContractRenewal
        fields = ['contract', 'previous_end_date', 'new_end_date', 'renewed_value', 'remarks']
        widgets = {
            'previous_end_date': forms.DateInput(attrs={'type': 'date'}),
            'new_end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class LicenseForm(BootstrapModelForm):
    class Meta:
        model = License
        fields = ['contract', 'software_name', 'license_key', 'seats', 'assigned_to', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
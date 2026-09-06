from django import forms
from .models import Vendor, VendorContact, VendorPerformance, VendorIssue, VendorEscalation


class BootstrapModelForm(forms.ModelForm):
    """Adds Bootstrap classes to every widget automatically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class VendorForm(BootstrapModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'registration_number', 'address', 'email', 'phone', 'status']


class VendorContactForm(BootstrapModelForm):
    class Meta:
        model = VendorContact
        fields = ['vendor', 'name', 'designation', 'email', 'phone', 'is_primary']


class VendorPerformanceForm(BootstrapModelForm):
    class Meta:
        model = VendorPerformance
        fields = ['vendor', 'evaluation_date', 'delivery_time_score',
                  'sla_compliance_score', 'quality_score', 'overall_rating', 'remarks']
        widgets = {'evaluation_date': forms.DateInput(attrs={'type': 'date'})}


class VendorIssueForm(BootstrapModelForm):
    class Meta:
        model = VendorIssue
        fields = ['vendor', 'title', 'description', 'severity', 'status']


class VendorEscalationForm(BootstrapModelForm):
    class Meta:
        model = VendorEscalation
        fields = ['issue', 'escalated_to', 'reason', 'resolution_notes', 'resolved']
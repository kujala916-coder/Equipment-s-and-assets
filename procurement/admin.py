from django.contrib import admin
from .models import (
    ProcurementPlan, ProcurementRequirement, Requisition,
    Procurement, ProcurementItem, TechnicalSpecification,
    TechnicalEvaluation, EvaluationItem
)


@admin.register(ProcurementPlan)
class ProcurementPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'period_type', 'fiscal_year', 'total_budget', 'created_at')
    list_filter = ('period_type', 'fiscal_year')
    search_fields = ('title', 'fiscal_year')


@admin.register(ProcurementRequirement)
class ProcurementRequirementAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'plan', 'category', 'quantity')
    list_filter = ('plan', 'category')
    search_fields = ('item_name',)


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'requirement', 'approved_by', 'approval_date')
    list_filter = ('approved_by',)


@admin.register(Procurement)
class ProcurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'tender_number', 'po_number', 'vendor',
                     'tender_publishing_date', 'total_value', 'created_at')
    list_filter = ('vendor',)
    search_fields = ('tender_number', 'po_number')


@admin.register(ProcurementItem)
class ProcurementItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'procurement', 'category', 'quantity',
                     'unit_price', 'total_price')
    list_filter = ('category',)
    search_fields = ('item_name',)


@admin.register(TechnicalSpecification)
class TechnicalSpecificationAdmin(admin.ModelAdmin):
    list_display = ('spec_name', 'procurement_item', 'required_value', 'mandatory')
    list_filter = ('mandatory',)


@admin.register(TechnicalEvaluation)
class TechnicalEvaluationAdmin(admin.ModelAdmin):
    list_display = ('procurement', 'vendor', 'evaluated_by', 'overall_result', 'evaluation_date')
    list_filter = ('overall_result',)


@admin.register(EvaluationItem)
class EvaluationItemAdmin(admin.ModelAdmin):
    list_display = ('specification', 'evaluation', 'offered_value', 'result')
    list_filter = ('result',)
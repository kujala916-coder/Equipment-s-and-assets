from django.contrib import admin
from .models import ProcurementPlan, ProcurementRequirement, Requisition, Procurement, ProcurementItem

admin.site.register(ProcurementPlan)
admin.site.register(ProcurementRequirement)
admin.site.register(Requisition)
admin.site.register(Procurement)
admin.site.register(ProcurementItem)
from django.contrib import admin
from .models import Contract, ContractRenewal, License, SLA

admin.site.register(Contract)
admin.site.register(ContractRenewal)
admin.site.register(License)
admin.site.register(SLA)
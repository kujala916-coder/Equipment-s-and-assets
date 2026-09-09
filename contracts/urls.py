from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.contract_list, name='contract_list'),
    path('renewals/', views.renewal_list, name='renewal_list'),
    path('licenses/add/', views.license_add, name='license_add'),
    path('licenses/renew/', views.license_renew, name='license_renew'),
    path('sla/add/', views.sla_add, name='sla_add'),
    path('sla/renew/', views.sla_renew, name='sla_renew'),
]
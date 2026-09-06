from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.contract_list, name='contract_list'),
    path('renewals/', views.renewal_list, name='renewal_list'),
    path('licenses/', views.license_list, name='license_list'),
]
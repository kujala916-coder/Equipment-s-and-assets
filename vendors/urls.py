from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('', views.vendor_list, name='vendor_list'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('performance/', views.performance_list, name='performance_list'),
    path('issues/', views.issue_list, name='issue_list'),
    path('escalations/', views.escalation_list, name='escalation_list'),
]
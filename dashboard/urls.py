from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('saved-reports/', views.saved_report_list, name='saved_report_list'),
]
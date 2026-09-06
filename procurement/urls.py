from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    path('plans/', views.plan_list, name='plan_list'),
    path('requirements/', views.requirement_list, name='requirement_list'),
    path('requisitions/', views.requisition_list, name='requisition_list'),
    path('', views.procurement_list, name='procurement_list'),
    path('items/', views.procurement_item_list, name='procurement_item_list'),
    path('specifications/', views.specification_list, name='specification_list'),
    path('evaluations/', views.evaluation_list, name='evaluation_list'),
    path('evaluation-items/', views.evaluation_item_list, name='evaluation_item_list'),
]
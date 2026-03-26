from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('leads/', views.leads_list, name='leads_list'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/update-status/', views.update_lead_status, name='update_lead_status'),
    path('leads/<int:pk>/export/', views.export_lead_pdf, name='export_lead_pdf'),
    path('followups/', views.follow_ups, name='follow_ups'),
    path('followups/<int:pk>/complete/', views.complete_followup, name='complete_followup'),
    path('reports/', views.reports, name='reports'),
    path('export-leads/', views.export_leads_excel, name='export_leads_excel'),
    path('import-leads/', views.import_leads_excel, name='import_leads_excel'),
    path('settings/', views.dashboard_settings, name='dashboard_settings'),
]
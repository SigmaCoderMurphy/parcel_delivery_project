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

    # Email Follow-up URLs
    path('emails/', views.email_followup_report, name='email_followup_report'),
    path('leads/<int:pk>/schedule-emails/', views.schedule_followup_emails, name='schedule_followup_emails'),
    path('leads/<int:pk>/send-email/', views.send_manual_email, name='send_manual_email'),
    
    # Lead PDF Export
    path('leads/<int:pk>/export-pdf/', views.export_lead_pdf, name='export_lead_pdf'),


    # NEW: PDF Quote Generation URLs
    path('leads/<int:pk>/create-quote/', views.create_quote, name='create_quote'),
    path('quotes/<int:pk>/view-pdf/', views.view_quote_pdf, name='view_quote_pdf'),
    path('quotes/<int:pk>/regenerate/', views.regenerate_quote_pdf, name='regenerate_quote_pdf'),
    path('quotes/<int:pk>/accept/', views.accept_quote, name='accept_quote'),
    
    # NEW: Call Tracking URLs
    path('calls/', views.call_logs, name='call_logs'),
    path('leads/<int:pk>/add-call/', views.add_call_log, name='add_call_log'),
    path('twilio-webhook/', views.twilio_call_webhook, name='twilio_webhook'),
]
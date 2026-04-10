from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('leads/', views.leads_list, name='leads_list'),
    path('leads/add/', views.add_lead, name='add_lead'),
    path('leads/<int:pk>/edit/', views.edit_lead, name='edit_lead'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/update-status/', views.update_lead_status, name='update_lead_status'),
    path('followups/', views.follow_ups, name='follow_ups'),
    path('followups/<int:pk>/complete/', views.complete_followup, name='complete_followup'),
    path('followups/create/', views.create_followup, name='create_followup'),
    path('reports/export-pdf/', views.export_reports_pdf, name='export_reports_pdf'),
    path('reports/', views.reports, name='reports'),
    path('custom-reports/', views.custom_reports, name='custom_reports'),
    path('export-leads/', views.export_leads_excel, name='export_leads_excel'),
    path('export-leads/csv/', views.export_leads_csv, name='export_leads_csv'),
    path('import-leads/', views.import_leads_excel, name='import_leads_excel'),
    path('settings/', views.dashboard_settings, name='dashboard_settings'),
    path('settings/logo.png', views.serve_logo, name='serve_logo'),

    # Settings: users / email templates / fleet / backup
    path('settings/users/<int:user_id>/active/', views.dashboard_toggle_user_active, name='dashboard_toggle_user_active'),
    path('settings/fleet/<int:vehicle_id>/active/', views.dashboard_toggle_fleet_active, name='dashboard_toggle_fleet_active'),
    path('settings/fleet/<int:vehicle_id>/delete/', views.dashboard_delete_fleet, name='dashboard_delete_fleet'),
    path('settings/fleet/<int:vehicle_id>/deactivate/', views.dashboard_deactivate_fleet, name='dashboard_deactivate_fleet'),
    path('settings/services/<int:service_id>/active/', views.dashboard_toggle_service_active, name='dashboard_toggle_service_active'),
    path('settings/services/<int:service_id>/delete/', views.dashboard_delete_service, name='dashboard_delete_service'),
    path('settings/email-templates/save/', views.dashboard_save_email_template, name='dashboard_save_email_template'),
    path('settings/backup/', views.dashboard_backup_database, name='dashboard_backup_database'),
    path('settings/restore/', views.dashboard_restore_database, name='dashboard_restore_database'),

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
    
    # NEW: Advanced Dashboard & Google Profile URLs
    path('chart-data/', views.chart_data, name='chart_data'),
    path('leads/<int:pk>/request-review/', views.request_google_review, name='request_google_review'),
]
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Lead, FollowUp, CommunicationLog, Quote, CallLog, CallAnalysis, ScheduledEmail

class LeadResource(resources.ModelResource):
    class Meta:
        model = Lead
        fields = ('id', 'company_name', 'contact_name', 'email', 'phone', 
                 'business_type', 'status', 'source', 'created_at')

@admin.register(Lead)
class LeadAdmin(ImportExportModelAdmin):
    resource_class = LeadResource
    list_display = ['company_name', 'contact_name', 'email', 'phone', 'business_type', 'status', 'source', 'created_at']
    list_filter = ['status', 'source', 'business_type', 'created_at']
    search_fields = ['company_name', 'contact_name', 'email', 'phone']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('company_name', 'contact_name', 'email', 'phone', 'alternative_phone')
        }),
        ('Business Details', {
            'fields': ('business_type', 'website', 'address', 'service_area')
        }),
        ('Lead Information', {
            'fields': ('status', 'source', 'assigned_to')
        }),
        ('Delivery Requirements', {
            'fields': ('delivery_frequency', 'typical_items', 'monthly_volume')
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes')
        }),
        ('Tracking', {
            'fields': ('created_at', 'updated_at', 'last_contacted')
        }),
    )

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['lead', 'followup_type', 'scheduled_date', 'is_completed', 'created_at']
    list_filter = ['followup_type', 'is_completed', 'scheduled_date']
    search_fields = ['lead__company_name', 'notes']

@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = ['lead', 'communication_type', 'direction', 'subject', 'created_at']
    list_filter = ['communication_type', 'direction', 'created_at']
    search_fields = ['lead__company_name', 'subject', 'content']

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'lead', 'amount', 'valid_until', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['quote_number', 'lead__company_name']

@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['caller_number', 'lead', 'call_type', 'call_duration', 'created_at']
    list_filter = ['call_type', 'created_at']
    search_fields = ['lead__company_name', 'caller_number', 'call_notes']
    readonly_fields = ['created_at', 'call_sid']

@admin.register(CallAnalysis)
class CallAnalysisAdmin(admin.ModelAdmin):
    list_display = ['call', 'sentiment_score', 'conversion_likelihood', 'created_at']
    list_filter = ['sentiment_score', 'created_at']
    search_fields = ['call__caller_number', 'keywords_extracted']
    readonly_fields = ['created_at']

@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(admin.ModelAdmin):
    list_display = ['lead', 'email_type', 'scheduled_date', 'sent', 'sent_at']
    list_filter = ['sent', 'scheduled_date', 'email_type']
    search_fields = ['lead__company_name', 'subject']
    readonly_fields = ['created_at', 'sent_at']
    
    fieldsets = (
        ('Email Information', {
            'fields': ('lead', 'email_type', 'subject')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'template_path')
        }),
        ('Status', {
            'fields': ('sent', 'sent_at', 'created_at')
        }),
    )